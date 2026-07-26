extends Node2D
## Level 1 (Feudal East arc, exterior). Loads its music at runtime, then
## GENERATES the level geometry/enemies/checkpoints from code so the layout
## can be long and easy to tweak (hand-authoring ~30k px of nodes in the
## .tscn is unmaintainable). Deterministic seed -> the layout is stable
## across runs. Programmer-art boxes until Pixellabs art exists.
##
## Layout is a left-to-right sequence of segments (flat stretches, brute
## arenas, platform stairs, wall-climb obstacles, wall-jump shafts, and a
## few bridged pits), sized for a ~10-minute clear once combat, climbing,
## and deaths are factored in. Tune LEVEL_LENGTH / segment mix / enemy
## density from playtest -- see README.

const MUSIC_PATH := "res://assets/audio/Iron Temple.mp3"
const HUMANOID := preload("res://scenes/enemies/EnemyHumanoid.tscn")
const FLYING := preload("res://scenes/enemies/EnemyFlying.tscn")
const BRUTE := preload("res://scenes/enemies/EnemyBrute.tscn")
const CHECKPOINT := preload("res://scenes/levels/Checkpoint.tscn")

const LEVEL_LENGTH := 90000.0     ## total horizontal extent (px)
const SURFACE_Y := 680.0          ## top of the ground plane
const FLOOR_CENTER_Y := 700.0
const FLOOR_HALF_H := 20.0
const CHECKPOINT_SPACING := 5000.0

const SOLID_COLOR := Color(0.28, 0.22, 0.14, 1)
const GROUND_COLOR := Color(0.2, 0.18, 0.12, 1)

@onready var music: AudioStreamPlayer = $Music

var _rng := RandomNumberGenerator.new()
var _next_checkpoint_x := CHECKPOINT_SPACING

func _ready() -> void:
	_start_music()
	_rng.seed = 20260725     # deterministic layout
	_generate_level()


# --- Music --------------------------------------------------------------
func _start_music() -> void:
	var stream := _load_mp3(MUSIC_PATH)
	if stream:
		stream.loop = true
		music.stream = stream
		music.play()


func _load_mp3(path: String) -> AudioStream:
	if not FileAccess.file_exists(path):
		push_warning("Level1: music file not found: %s" % path)
		return null
	var f := FileAccess.open(path, FileAccess.READ)
	var stream := AudioStreamMP3.new()
	stream.data = f.get_buffer(f.get_length())
	return stream


# --- Generation ---------------------------------------------------------
func _generate_level() -> void:
	# Opening flat runway so the player gets their footing before the first
	# threat (the Ninja starts at x=100 in the .tscn).
	var x := 0.0
	x = _seg_flat(x, 1500.0, 1)

	# Walk the level laying one segment at a time until we reach the end.
	while x < LEVEL_LENGTH:
		_maybe_checkpoint(x)
		var kind := _rng.randi_range(0, 5)
		match kind:
			0: x = _seg_flat(x, _rng.randf_range(1200.0, 1800.0), _rng.randi_range(1, 3))
			1: x = _seg_arena(x)
			2: x = _seg_stairs(x)
			3: x = _seg_wall_climb(x)
			4: x = _seg_wall_jump(x)
			5: x = _seg_pit(x)

	# Closing stretch leads into a solid finish plaza + win trigger.
	x = _seg_flat(x, 1000.0, 0)
	_add_finish(x)


func _maybe_checkpoint(x: float) -> void:
	if x >= _next_checkpoint_x:
		_add_checkpoint(x)
		_next_checkpoint_x += CHECKPOINT_SPACING


# --- Segment builders (each lays floor + features, returns the new x) ----
func _seg_flat(x: float, width: float, humanoids: int) -> float:
	_floor(x, x + width)
	for i in humanoids:
		_spawn(HUMANOID, x + width * (float(i) + 1.0) / (humanoids + 1), 640.0)
	if _rng.randf() < 0.5:
		_spawn(FLYING, x + width * 0.5, _rng.randf_range(420.0, 500.0))
	return x + width


func _seg_arena(x: float) -> float:
	# A fight chokepoint: a brute flanked by a couple of humanoids.
	var width := 1400.0
	_floor(x, x + width)
	_spawn(BRUTE, x + width * 0.5, 600.0)
	_spawn(HUMANOID, x + width * 0.25, 640.0)
	_spawn(HUMANOID, x + width * 0.75, 640.0)
	if _rng.randf() < 0.6:
		_spawn(FLYING, x + width * 0.5, 440.0)
	return x + width


func _seg_stairs(x: float) -> float:
	# Three ascending platforms over a continuous floor, with a flyer to
	# contest the climb.
	var width := 1100.0
	_floor(x, x + width)
	_platform(x + 300.0, 600.0, 90.0)
	_platform(x + 550.0, 520.0, 90.0)
	_platform(x + 800.0, 440.0, 90.0)
	_spawn(FLYING, x + 650.0, 380.0)
	return x + width


func _seg_wall_climb(x: float) -> float:
	# A tall wall the Ninja must wall-climb over. Floor stays continuous so a
	# missed climb is a retry, not a death. A landing platform sits on top.
	var width := 800.0
	_floor(x, x + width)
	_wall(x + width * 0.5, 260.0)
	_platform(x + width * 0.5 + 120.0, 440.0, 90.0)
	_spawn(HUMANOID, x + width - 120.0, 640.0)
	return x + width


func _seg_wall_jump(x: float) -> float:
	# Two parallel walls with a gap to wall-jump up between. Floor below so a
	# miss is a retry. Flyer harasses from above.
	var width := 800.0
	_floor(x, x + width)
	_wall(x + width * 0.5 - 90.0, 240.0)
	_wall(x + width * 0.5 + 90.0, 240.0)
	_spawn(FLYING, x + width * 0.5, 380.0)
	return x + width


func _seg_pit(x: float) -> float:
	# A real fall hazard: floor, a gap bridged by a mid platform, floor. The
	# gaps are kept jump-crossable; falling in respawns at the last checkpoint.
	var width := 1200.0
	_floor(x, x + 400.0)
	_platform(x + 600.0, 640.0, 90.0)   # bridge island
	_floor(x + 800.0, x + width)
	if _rng.randf() < 0.5:
		_spawn(FLYING, x + 600.0, 450.0)
	return x + width


# --- Primitive helpers --------------------------------------------------
func _floor(x0: float, x1: float) -> void:
	var w := x1 - x0
	_solid(Vector2((x0 + x1) * 0.5, FLOOR_CENTER_Y), Vector2(w, FLOOR_HALF_H * 2.0), GROUND_COLOR)


func _platform(cx: float, cy: float, half_w: float) -> void:
	_solid(Vector2(cx, cy), Vector2(half_w * 2.0, 24.0), SOLID_COLOR)


func _wall(cx: float, height: float) -> void:
	# Wall rises from the ground surface up by `height`.
	_solid(Vector2(cx, SURFACE_Y - height * 0.5), Vector2(24.0, height), SOLID_COLOR)


func _solid(center: Vector2, size: Vector2, color: Color) -> void:
	var body := StaticBody2D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	body.position = center
	var cs := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = size
	cs.shape = shape
	body.add_child(cs)
	var vis := Polygon2D.new()
	var hw := size.x * 0.5
	var hh := size.y * 0.5
	vis.polygon = PackedVector2Array([
		Vector2(-hw, -hh), Vector2(hw, -hh), Vector2(hw, hh), Vector2(-hw, hh)])
	vis.color = color
	body.add_child(vis)
	add_child(body)


func _spawn(scene: PackedScene, x: float, y: float) -> void:
	var e := scene.instantiate()
	e.position = Vector2(x, y)
	add_child(e)


func _add_checkpoint(x: float) -> void:
	var cp := CHECKPOINT.instantiate()
	cp.position = Vector2(x, 630.0)
	add_child(cp)


var _finished := false

func _add_finish(x: float) -> void:
	# Real finish: a solid plaza so the level ends on standable ground (not a
	# cliff you fall off), a torii gate marking the goal, and an Area2D across
	# the gate that fires the win when the player walks through it.
	var plaza_end := x + 1400.0
	_floor(x, plaza_end)
	var gate_x := x + 500.0
	_add_gate_visual(gate_x)

	var area := Area2D.new()
	area.position = Vector2(gate_x, SURFACE_Y - 100.0)
	area.collision_layer = 0
	area.collision_mask = 2          # detect the player (player is on layer 2)
	var cs := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(60.0, 200.0)
	cs.shape = shape
	area.add_child(cs)
	area.body_entered.connect(_on_reached_finish)
	add_child(area)


func _add_gate_visual(x: float) -> void:
	# Decorative torii-style marker at the finish.
	var gate := Node2D.new()
	gate.position = Vector2(x, SURFACE_Y)
	var vis := Polygon2D.new()
	vis.color = Color(0.2, 0.15, 0.1, 1)
	vis.polygon = PackedVector2Array([
		Vector2(-70, 0), Vector2(-50, 0), Vector2(-50, -180), Vector2(-70, -180),
		Vector2(70, 0), Vector2(50, 0), Vector2(50, -180), Vector2(70, -180),
		Vector2(-60, -160), Vector2(60, -160), Vector2(-60, -130), Vector2(60, -130)])
	gate.add_child(vis)
	add_child(gate)


func _on_reached_finish(body: Node) -> void:
	if _finished or not body.is_in_group("player"):
		return
	_finished = true
	# Freeze the player in place and show the win banner. A real level-complete
	# flow (score, next-level load) is a later pass -- see README open items.
	if body.has_method("set_physics_process"):
		body.set_physics_process(false)
	if body is CharacterBody2D:
		body.velocity = Vector2.ZERO
	_show_level_complete()


func _show_level_complete() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 100
	var dim := ColorRect.new()
	dim.color = Color(0.0, 0.0, 0.0, 0.55)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(dim)
	var label := Label.new()
	label.text = "LEVEL COMPLETE"
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.set_anchors_preset(Control.PRESET_FULL_RECT)
	label.add_theme_font_size_override("font_size", 72)
	label.add_theme_color_override("font_color", Color(0.9, 0.8, 0.4))
	layer.add_child(label)
	add_child(layer)
