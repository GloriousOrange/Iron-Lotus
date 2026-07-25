extends Enemy
## Large creature demon -- a heavy, dangerous mini-threat (not a boss). Slow
## but high HP and hard-hitting, and NOT light, so ninja stars only stun/chip
## it rather than killing it outright. Telegraphs a wind-up before its heavy
## swing. Programmer-art large capsule until Pixellabs sprites exist.

const GRAVITY := 1400.0
const PATROL_SPEED := 35.0
const CHASE_SPEED := 75.0
const AGGRO_RANGE := 320.0
const ATTACK_RANGE := 60.0
const ATTACK_WINDUP := 0.5     ## telegraph before the hit lands
const ATTACK_COOLDOWN := 1.8

@onready var ledge_check: RayCast2D = $LedgeCheck
@onready var wall_check: RayCast2D = $WallCheck
@onready var visual: Polygon2D = $Visual

var _dir := -1
var _attack_cd := 0.0
var _winding_up := false
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

	if is_stunned() or _winding_up:
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
		# Deadzone-gated so a near-zero reading never collapses facing to 0
		# (see feedback on the self-referential scale-flip bug).
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

	scale.x = abs(scale.x) * _dir
	move_and_slide()


func _attack() -> void:
	_attack_cd = ATTACK_COOLDOWN
	_winding_up = true
	var base := visual.color
	visual.color = Color(0.9, 0.3, 0.1, 1)   # flash red during the telegraph
	await get_tree().create_timer(ATTACK_WINDUP).timeout
	if not is_instance_valid(self):
		return
	visual.color = base
	_winding_up = false
	# Only connects if the player is still in range when the swing lands.
	if _player and is_instance_valid(_player) \
			and abs(_player.global_position.x - global_position.x) <= ATTACK_RANGE \
			and _player.has_method("take_hit"):
		_player.take_hit(contact_damage)
