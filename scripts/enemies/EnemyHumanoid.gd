extends Enemy
## Placeholder ground demon: patrols a platform, turns around at ledges/walls,
## chases the player within aggro range, melee-attacks on contact range.
## Programmer-art capsule visuals until Pixellabs sprites exist.

const GRAVITY := 1400.0
const PATROL_SPEED := 60.0
const CHASE_SPEED := 110.0
const AGGRO_RANGE := 220.0
const ATTACK_RANGE := 34.0
const ATTACK_COOLDOWN := 1.0
const VISUAL_SCALE_X := 1.0   ## fixed magnitude -- never derived from itself

@onready var ledge_check: RayCast2D = $LedgeCheck
@onready var wall_check: RayCast2D = $WallCheck

var _dir := -1
var _attack_cd := 0.0
var _player: Node2D = null

func _ready() -> void:
	super._ready()
	var players := get_tree().get_nodes_in_group("player")
	if players.size() > 0:
		_player = players[0]


func _physics_process(delta: float) -> void:
	_process_stun(delta)
	if not is_on_floor():
		velocity.y += GRAVITY * delta
	else:
		velocity.y = 0.0

	if is_stunned():
		velocity.x = 0.0
		move_and_slide()
		return

	_attack_cd = max(0.0, _attack_cd - delta)

	var to_player := 0.0
	var in_aggro := false
	if _player:
		to_player = _player.global_position.x - global_position.x
		in_aggro = global_position.distance_to(_player.global_position) <= AGGRO_RANGE

	if in_aggro:
		# Deadzone-gated: a near-zero `to_player` (enemy almost exactly aligned
		# with the player) must never collapse `_dir` to 0 -- that would
		# permanently zero `scale.x` below (self-referential formula) and
		# freeze/hide the enemy for good. Keep the previous direction instead.
		if to_player > 1.0:
			_dir = 1
		elif to_player < -1.0:
			_dir = -1
		velocity.x = _dir * CHASE_SPEED
		if abs(to_player) <= ATTACK_RANGE and _attack_cd <= 0.0:
			_attack()
	else:
		velocity.x = _dir * PATROL_SPEED
		if is_on_floor() and (not ledge_check.is_colliding() or wall_check.is_colliding()):
			_dir *= -1

	scale.x = VISUAL_SCALE_X * _dir

	move_and_slide()


func _attack() -> void:
	_attack_cd = ATTACK_COOLDOWN
	if _player and _player.has_method("take_hit"):
		_player.take_hit(contact_damage)
