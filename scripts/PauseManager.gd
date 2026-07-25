extends Node
## Toggles the pause state on the gamepad Start button / Escape. Runs even
## while the tree is paused (process_mode ALWAYS) so it can un-pause itself.
## No pause menu UI yet -- just freezes/unfreezes gameplay (see README open
## items for a real pause screen).

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("pause"):
		get_tree().paused = not get_tree().paused
