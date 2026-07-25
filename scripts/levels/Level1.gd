extends Node2D
## Level 1 (Feudal East arc, exterior). Loads its music at runtime (bytes ->
## AudioStreamMP3) so there's no editor-import step, same pattern used in
## Lawn of the Dead.

const MUSIC_PATH := "res://assets/audio/Iron Temple.mp3"

@onready var music: AudioStreamPlayer = $Music

func _ready() -> void:
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
