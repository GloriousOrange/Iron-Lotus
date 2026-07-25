extends Enemy
## Placeholder flying demon: bobs/patrols in the air, dives at the player when
## in range then returns to its patrol altitude. No gravity -- true flight.

const PATROL_SPEED := 80.0
const DIVE_SPEED := 220.0
const AGGRO_RANGE := 260.0
const ATTACK_RANGE := 30.0
const ATTACK_COOLDOWN := 1.2
const BOB_HEIGHT := 14.0
const BOB_SPEED := 2.0
const VISUAL_SCALE_X := 1.0   ## fixed magnitude -- never derived from itself

var _home_y := 0.0
var _t := 0.0
var _dir := -1
var _attack_cd := 0.0
var _player: Node2D = null

func _ready() -> void:
	super._ready()
	_home_y = global_position.y
	var players := get_tree().get_nodes_in_group("player")
	if players.size() > 0:
		_player = players[0]


func _physics_process(delta: float) -> void:
	_process_stun(delta)
	_t += delta
	_attack_cd = max(0.0, _attack_cd - delta)

	if is_stunned():
		velocity = Vector2.ZERO
		move_and_slide()
		return

	var in_aggro := _player != null and global_position.distance_to(_player.global_position) <= AGGRO_RANGE

	if in_aggro:
		var to_player: Vector2 = _player.global_position - global_position
		velocity = to_player.normalized() * DIVE_SPEED
		if to_player.length() <= ATTACK_RANGE and _attack_cd <= 0.0:
			_attack_cd = ATTACK_COOLDOWN
			if _player.has_method("take_hit"):
				_player.take_hit(contact_damage)
	else:
		velocity.x = _dir * PATROL_SPEED
		velocity.y = cos(_t * BOB_SPEED) * BOB_HEIGHT - (global_position.y - _home_y)

	# Deadzone-gated so a near-vertical dive (velocity.x close to 0) can never
	# collapse the facing direction to 0 -- that would permanently zero
	# scale.x via a self-referential formula and hide the enemy for good.
	# Keep the previous facing direction instead of flipping on tiny values.
	if velocity.x > 1.0:
		_dir = 1
	elif velocity.x < -1.0:
		_dir = -1
	scale.x = VISUAL_SCALE_X * _dir

	move_and_slide()
