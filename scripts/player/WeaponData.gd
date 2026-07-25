class_name WeaponData
extends Resource
## Placeholder per-weapon stats for the Ninja's melee loadout. Numbers are
## first-pass guesses for feel-testing, not balanced -- see README.md open
## items for the full weapon list per character.

@export var weapon_name: String = ""
@export var damage: float = 10.0
@export var attack_range: float = 40.0     ## px reach of the melee hitbox
@export var attack_cooldown: float = 0.4   ## seconds between swings
@export var can_block: bool = false        ## staff/katana only, per README
