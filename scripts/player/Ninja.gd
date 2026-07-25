extends CharacterBody2D
## Kageharu (Ninja) — agile skill-fighter. Wall-climb (unique among the
## melee fighters), wall-jump, dodge-roll, two independently-attackable
## melee weapons (Attack1/Attack2, no swap needed), one locked-in ranged
## loadout (Attack3, limited ammo, passive regen). Placeholder capsule
## visuals + placeholder weapon stats -- see README.md open items for the
## real weapon feel pass.
##
## Controller mapping (see InputSetup.gd): Attack1/2 = the two equipped
## melee weapons, Attack3 = ranged throw, Block/Dodge = shoulder buttons.

const GRAVITY := 1400.0
const MOVE_SPEED := 220.0
const JUMP_VELOCITY := -520.0
const WALL_SLIDE_MAX_FALL := 80.0
const WALL_CLIMB_SPEED := 140.0
const WALL_JUMP_VELOCITY := Vector2(300.0, -480.0)
const DODGE_SPEED := 420.0
const DODGE_DURATION := 0.25
const DODGE_COOLDOWN := 0.6
const DODGE_IFRAMES := 0.2
const VISUAL_SCALE_X := 1.0       ## fixed magnitude -- never derived from itself
const MELEE_HITBOX_OFFSET_X := 23.0

const MAX_HEALTH := 100.0
const THROW_AMMO_MAX := 8
const THROW_AMMO_REGEN_SECONDS := 3.0   ## +1 ammo every N seconds
const NINJA_STAR_SCENE := preload("res://scenes/player/NinjaStar.tscn")

@onready var melee_hitbox: Area2D = $MeleeHitbox
@onready var melee_hitbox_shape: CollisionShape2D = $MeleeHitbox/CollisionShape2D
@onready var sprite: Node2D = $Visual

var health := MAX_HEALTH
var facing := 1   ## 1 = right, -1 = left

# --- Loadout (loadout-select screen is a later pass; hardcoded for now) ---
var melee_weapons: Array[WeaponData] = []
var equipped_melee: Array[int] = [0, 3]   ## indices into melee_weapons: katana + nun-chucks

var throw_ammo := THROW_AMMO_MAX
var _ammo_regen_t := 0.0

# --- Transient state ---
var _attack_cd := 0.0
var _active_weapon: WeaponData = null   ## weapon used by the swing currently open
var _dodging := false
var _dodge_t := 0.0
var _dodge_cd := 0.0
var _iframes_t := 0.0
var _blocking := false
var _respawn_point: Vector2


func _ready() -> void:
	add_to_group("player")
	_build_weapons()
	melee_hitbox.monitoring = false
	melee_hitbox.body_entered.connect(_on_melee_hit)
	_respawn_point = global_position


func set_checkpoint(pos: Vector2) -> void:
	_respawn_point = pos


func _build_weapons() -> void:
	# Placeholder stats -- katana/staff can block per README; sais/nun-chucks can't.
	var katana := WeaponData.new()
	katana.weapon_name = "Katana"
	katana.damage = 14.0
	katana.attack_range = 46.0
	katana.attack_cooldown = 0.35
	katana.can_block = true

	var sais := WeaponData.new()
	sais.weapon_name = "Double Sais"
	sais.damage = 10.0
	sais.attack_range = 32.0
	sais.attack_cooldown = 0.2
	sais.can_block = false

	var staff := WeaponData.new()
	staff.weapon_name = "Staff"
	staff.damage = 11.0
	staff.attack_range = 56.0
	staff.attack_cooldown = 0.4
	staff.can_block = true

	var nunchucks := WeaponData.new()
	nunchucks.weapon_name = "Nun-chucks"
	nunchucks.damage = 9.0
	nunchucks.attack_range = 38.0
	nunchucks.attack_cooldown = 0.18
	nunchucks.can_block = false

	melee_weapons = [katana, sais, staff, nunchucks]


func _can_block_loadout() -> bool:
	# Blocking is available if EITHER equipped melee weapon supports it (you
	# don't need to have just swung it) -- see README's block-gating rule.
	for i in equipped_melee:
		if melee_weapons[i].can_block:
			return true
	return false


func _physics_process(delta: float) -> void:
	_iframes_t = max(0.0, _iframes_t - delta)
	_attack_cd = max(0.0, _attack_cd - delta)
	_dodge_cd = max(0.0, _dodge_cd - delta)
	_regen_ammo(delta)

	if _dodging:
		_process_dodge(delta)
		move_and_slide()
		return

	_blocking = Input.is_action_pressed("block") and _can_block_loadout() and is_on_floor()

	var on_wall := is_on_wall() and not is_on_floor()
	var climbing := on_wall and Input.is_action_pressed("move_up")

	if climbing:
		velocity.y = -WALL_CLIMB_SPEED
	elif not is_on_floor():
		velocity.y += GRAVITY * delta
		if on_wall and velocity.y > WALL_SLIDE_MAX_FALL:
			velocity.y = WALL_SLIDE_MAX_FALL
	else:
		velocity.y = 0.0

	if Input.is_action_just_pressed("jump"):
		if is_on_floor():
			velocity.y = JUMP_VELOCITY
		elif on_wall:
			var n := get_wall_normal()
			velocity.x = n.x * WALL_JUMP_VELOCITY.x
			velocity.y = WALL_JUMP_VELOCITY.y
			facing = -1 if n.x < 0.0 else 1

	if _blocking:
		velocity.x = 0.0
	elif not climbing:
		var input_dir := Input.get_axis("move_left", "move_right")
		velocity.x = input_dir * MOVE_SPEED
		# Deadzone-gated so gamepad axis noise near zero can never register as a
		# direction change -- facing must only ever be +1 or -1, never 0 (a
		# stray 0 here used to permanently zero out the sprite's scale, see
		# _update_facing).
		if input_dir > 0.2:
			facing = 1
		elif input_dir < -0.2:
			facing = -1
	else:
		velocity.x = 0.0

	_update_facing()

	if Input.is_action_just_pressed("dodge") and _dodge_cd <= 0.0 and is_on_floor():
		_start_dodge()
	elif Input.is_action_just_pressed("attack1") and _attack_cd <= 0.0:
		_attack(melee_weapons[equipped_melee[0]])
	elif Input.is_action_just_pressed("attack2") and _attack_cd <= 0.0:
		_attack(melee_weapons[equipped_melee[1]])
	elif Input.is_action_just_pressed("attack3") and throw_ammo > 0:
		_throw_star()

	move_and_slide()


func _update_facing() -> void:
	sprite.scale.x = VISUAL_SCALE_X * facing
	melee_hitbox.position.x = MELEE_HITBOX_OFFSET_X * facing


func _start_dodge() -> void:
	_dodging = true
	_dodge_t = DODGE_DURATION
	_dodge_cd = DODGE_COOLDOWN
	_iframes_t = DODGE_IFRAMES
	velocity = Vector2(facing * DODGE_SPEED, 0.0)


func _process_dodge(delta: float) -> void:
	_dodge_t -= delta
	if _dodge_t <= 0.0:
		_dodging = false
		velocity.x = 0.0
	if not is_on_floor():
		velocity.y += GRAVITY * delta


func _attack(w: WeaponData) -> void:
	_attack_cd = w.attack_cooldown
	_active_weapon = w
	if melee_hitbox_shape.shape is RectangleShape2D:
		melee_hitbox_shape.shape.size = Vector2(w.attack_range, 40.0)
	melee_hitbox.position.x = abs(w.attack_range * 0.5) * facing
	melee_hitbox.monitoring = true
	await get_tree().create_timer(0.08).timeout
	melee_hitbox.monitoring = false


func _on_melee_hit(body: Node) -> void:
	if body is Enemy and _active_weapon != null:
		body.take_damage(_active_weapon.damage)


func _throw_star() -> void:
	throw_ammo -= 1
	var star := NINJA_STAR_SCENE.instantiate()
	get_parent().add_child(star)
	star.global_position = global_position
	star.direction = Vector2(facing, 0.0)


func _regen_ammo(delta: float) -> void:
	if throw_ammo >= THROW_AMMO_MAX:
		return
	_ammo_regen_t += delta
	if _ammo_regen_t >= THROW_AMMO_REGEN_SECONDS:
		_ammo_regen_t = 0.0
		throw_ammo += 1


func take_hit(amount: float) -> void:
	if _iframes_t > 0.0:
		return
	if _blocking:
		return
	health -= amount
	if health <= 0.0:
		_die()


func _die() -> void:
	# Placeholder: real lives system (limited retries per level) is a later
	# pass -- see README. For now, just respawn at the last checkpoint.
	health = MAX_HEALTH
	velocity = Vector2.ZERO
	global_position = _respawn_point
