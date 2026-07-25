extends Area2D
## Simple checkpoint marker: on first player contact, updates the player's
## respawn point and switches to its "activated" color. No lives/UI yet --
## see README's Health/Lives/Checkpoints section for the fuller system.

@export var activated_color := Color(0.85, 0.7, 0.2, 1)
@onready var visual: Polygon2D = $Visual

var _activated := false

func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node) -> void:
	if _activated:
		return
	if body.is_in_group("player") and body.has_method("set_checkpoint"):
		body.set_checkpoint(global_position)
		_activated = true
		visual.color = activated_color
