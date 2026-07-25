extends Area2D
## Thrown ninja-star projectile: stuns for ~1s, or kills light enemies
## outright (per README). Straight-line travel, despawns after range/lifetime.

const SPEED := 500.0
const LIFETIME := 1.2
const STUN_DURATION := 1.0

var direction := Vector2.RIGHT
var _life := 0.0

func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _physics_process(delta: float) -> void:
	position += direction * SPEED * delta
	_life += delta
	if _life >= LIFETIME:
		queue_free()


func _on_body_entered(body: Node) -> void:
	if body is Enemy:
		body.take_damage(0.0, true)
		if is_instance_valid(body):
			body.apply_stun(STUN_DURATION)
	queue_free()
