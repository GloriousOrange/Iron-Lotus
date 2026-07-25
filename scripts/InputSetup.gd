extends Node
## Defines all gameplay input actions in code (not project.godot) so a future
## rebind menu just rewrites these at runtime, same pattern as Lawn of the Dead.
## Player 1 only for now -- co-op device assignment (2 gamepads) is a later pass.
##
## Generic-gamepad control scheme (Godot's joypad button constants are already
## abstracted across Xbox/PlayStation/generic layouts):
##   Jump ............ A / bottom face button
##   Attack 1 ......... X / left face button  (melee slot A, or caster melee)
##   Attack 2 ......... Y / top face button    (melee slot B, or secondary A)
##   Attack 3 ......... B / right face button  (ranged/secondary, or secondary B)
##   Block ............ Left shoulder (only does anything if the loadout allows it)
##   Dodge-roll ....... Right shoulder
##   Pause ............ Start
## Skill fighters (Ninja/Knight/Viking) use Attack 1/2 for their two equipped
## melee weapons and Attack 3 for the ranged throw. Casters (Kimono Girl/
## Priest/Seidr Witch) use Attack 1 for melee and Attack 2/3 for their two
## secondary items (fans/books) -- see README.md.

func _ready() -> void:
	_def_action("move_left",  [_key(KEY_A), _key(KEY_LEFT),  _joyb(JOY_BUTTON_DPAD_LEFT),  _joya(JOY_AXIS_LEFT_X, -1.0)])
	_def_action("move_right", [_key(KEY_D), _key(KEY_RIGHT), _joyb(JOY_BUTTON_DPAD_RIGHT), _joya(JOY_AXIS_LEFT_X,  1.0)])
	_def_action("move_up",    [_key(KEY_W), _key(KEY_UP),    _joyb(JOY_BUTTON_DPAD_UP),    _joya(JOY_AXIS_LEFT_Y, -1.0)])
	_def_action("move_down",  [_key(KEY_S), _key(KEY_DOWN),  _joyb(JOY_BUTTON_DPAD_DOWN),  _joya(JOY_AXIS_LEFT_Y,  1.0)], 0.3)
	_def_action("jump",    [_key(KEY_SPACE),  _joyb(JOY_BUTTON_A)])
	_def_action("attack1", [_key(KEY_J),      _joyb(JOY_BUTTON_X)])
	_def_action("attack2", [_key(KEY_K),      _joyb(JOY_BUTTON_Y)])
	_def_action("attack3", [_key(KEY_L),      _joyb(JOY_BUTTON_B)])
	_def_action("block",   [_key(KEY_SHIFT),  _joyb(JOY_BUTTON_LEFT_SHOULDER)])
	_def_action("dodge",   [_key(KEY_CTRL),   _joyb(JOY_BUTTON_RIGHT_SHOULDER)])
	_def_action("pause",   [_key(KEY_ESCAPE), _joyb(JOY_BUTTON_START)])


func _def_action(name: String, events: Array, deadzone := 0.5) -> void:
	if InputMap.has_action(name):
		InputMap.erase_action(name)
	InputMap.add_action(name, deadzone)
	for e in events:
		InputMap.action_add_event(name, e)


func _key(kc: int) -> InputEventKey:
	var e := InputEventKey.new()
	e.physical_keycode = kc
	return e


func _joyb(b: int) -> InputEventJoypadButton:
	var e := InputEventJoypadButton.new()
	e.button_index = b
	return e


func _joya(axis: int, val: float) -> InputEventJoypadMotion:
	var e := InputEventJoypadMotion.new()
	e.axis = axis
	e.axis_value = val
	return e
