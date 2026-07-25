class_name Enemy
extends CharacterBody2D
## Shared base for all enemy types: health, damage, stun, death. Concrete
## enemies (EnemyHumanoid, EnemyFlying, ...) extend this and implement their
## own movement/AI in _physics_process.

signal died(enemy: Enemy)

@export var max_health: float = 30.0
@export var is_light: bool = true   ## light enemies die outright to a ninja star
@export var contact_damage: float = 10.0

var health: float
var stun_timer: float = 0.0

func _ready() -> void:
	health = max_health


func is_stunned() -> bool:
	return stun_timer > 0.0


func apply_stun(duration: float) -> void:
	stun_timer = max(stun_timer, duration)


func take_damage(amount: float, instakill: bool = false) -> void:
	if instakill and is_light:
		health = 0.0
	else:
		health -= amount
	if health <= 0.0:
		die()


func die() -> void:
	died.emit(self)
	queue_free()


func _process_stun(delta: float) -> void:
	if stun_timer > 0.0:
		stun_timer = max(0.0, stun_timer - delta)
