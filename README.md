# Iron Lotus (working title)

A dark, gritty 2D side-scrolling action platformer with local couch co-op.
Built in Godot 4.

This README is the living game design document. It will be updated as the
design evolves — nothing here is final until we start locking systems down
for implementation.

## Status

**Concept/design phase.** No code, no repo history yet — this is the design
reference the team (4 friends + the project owner, all collaborating via
Claude) will build from once the concept is fleshed out.

## Pillars

- Dark, gritty tone. Industrial metal instrumental soundtrack (already
  produced via Suno).
- Visually inspired by *Abathor*: multi-layer parallax backgrounds (e.g.
  distant crashing waves scrolling slower than the walkable foreground).
- Hard but fair — Souls-adjacent difficulty via enemy patterns and precise
  play, not stat-checks.
- Local couch co-op, multiple very differently-controlled characters
  (currently Ninja, Knight, Kimono Girl).
- Godot 4, PC-only for the initial build (no online netcode, no mobile).

## Characters

### Ninja
- Agile: wall-climb, slide, wall-jump, dodge-roll.
- Primary (melee) — pick **two** per level, swappable mid-level via button:
  **katana, double sais, staff, nun-chucks**.
- Secondary (ranged, limited ammo) — pick **one** per level, locked for the
  whole level: **ninja stars, giant ninja stars, throwing spikes**.
- Blocking: only available with **staff** or **katana**. No blocking with
  nun-chucks or sais — those loadouts rely on the universal dodge-roll
  instead.
- Ranged use: stuns for ~1s, or kills light enemies outright.

### Knight
- Armored, no wall-climb, but can wall-jump. Dodge-roll available
  regardless of loadout.
- Primary (melee) — pick **two** per level, swappable mid-level via button:
  - One-handed + shield: **sword, mace, flail** (each paired with a shield)
  - Two-handed (no shield): **maul, battle axe**
- Secondary (ranged, limited ammo) — pick **one** per level, locked for the
  whole level: **bow and arrows, crossbow, throwing axes**.
- Shield block is aimable in three directions via the block button: held
  forward (standard block), raised overhead (anti-aerial-attack block), or
  angled diagonally. Only available on one-handed+shield loadouts.

### Kimono Girl (elemental spellcaster)
- Melee: **chopsticks or hairpin** (TBD which, or possibly both as
  alternative skins/options) — elemental, single loadout for the whole
  level. Infinite uses, but each spell configuration has its own cooldown
  period (stronger spells → longer cooldown). Uses the same combo matrix
  as the fans (below), configured independently.
- Ranged: **two fans**, each independently configured with its own spell,
  swappable mid-level via a button press. Fans draw from a shared **mana
  pool** that regenerates over time.
- **Spell-building system**: at the start of a level, the player builds a
  spell for the melee weapon and each of the two fans independently by
  selecting two elements (repeats allowed) from **Fire, Water, Wind,
  Earth**, plus a delivery mode: **Instant**, **Charged**, or
  **Channeled**. Element order never matters (Fire+Water == Water+Fire).

#### Elemental Combo Matrix (complete: 10 pairs x 3 modes = 30 spells)

**Pure pairs:**

| Element | Instant | Charged | Channeled |
|---|---|---|---|
| Fire+Fire | Quick fireball / fire-slash burst | Slow-charging fireball, heavy damage | Continuous flamethrower |
| Water+Water | Water-jet burst, short knockback | High-pressure piercing water spike | Continuous water stream (pushback; douses fire hazards) |
| Wind+Wind (Tornado) | Gust burst, knockback/interrupt | Small tornado launched forward, pulls enemies in then damages | Aimable vortex anchored in front of the player — can be pointed forward, upward, or diagonally; continuously juggles/damages light enemies caught inside |
| Earth+Earth | Quick rock-shard throw | Heavy AoE boulder slam | Rising stone spikes / stationary rock wall (defensive cover) |

**Mixed pairs:**

| Elements | Theme | Instant | Charged | Channeled |
|---|---|---|---|---|
| Fire+Water | Steam | Steam burst (brief blind + minor damage) | Pressurized steam blast, armor-piercing cone | Lingering steam cloud (DOT + blocks enemy line of sight) |
| Fire+Wind | Fire Tornado | Small spinning fire funnel, brief AoE burn | Larger fire tornado launched forward, heavy sustained burn | Standing fire tornado that persists and travels slowly, major area-denial hazard |
| Fire+Earth | Lava | Molten rock lob, small AoE burn | Ground-targeted eruption, telegraphed heavy hit | Lava flow — persistent ground hazard, area denial |
| Water+Wind | Ice | Ice shard throw, chance to slow/freeze | Ice-spike wall (doubles as temporary platform/barrier) | Freezing wind beam, DOT + chance to fully freeze/stun |
| Water+Earth | Plants | Thorn/vine whip strike, brief snare on hit | Summoned root trap, ground-targeted entangle/immobilize | Growing vine field — continuous entangle + chip damage in an area |
| Wind+Earth | Sandstorm | Sand burst, brief accuracy/vision debuff on enemies | Compressed dust bomb, delayed burst + heavy knockback | Persistent sandstorm vortex, DOT + obscures vision |

The same matrix drives both the melee weapon and the two fans, but all
three are configured independently at level start (3 separate loadout
choices: melee spell, fan 1 spell, fan 2 spell). Melee is cooldown-based
(per-spell cooldown, infinite uses); fans draw from the shared mana pool.

**Still open:**
- Melee-specific meaning of Instant/Charged/Channeled — effects above were
  written with fan/ranged delivery in mind and may need adjusting for
  melee range/feel.
- Balance pass: some effects lean utility/traversal (ice platform, tornado
  updraft) rather than damage — confirm that's desired variety.
- Numeric tuning (damage, DOT ticks, freeze/slow duration, mana cost/
  cooldown per mode) — concept/effect level only for now.
- Whether chopsticks vs. hairpin is a real choice (two distinct melee
  weapons) or just a cosmetic/flavor decision for one weapon.

## Universal Combat Rules

- **Three-way aim**: some directional abilities can be aimed forward,
  upward, or diagonally (e.g. the Knight's shield block stance, the Kimono
  Girl's channeled Wind+Wind tornado). Worth keeping as a shared, reusable
  input pattern rather than a one-off per ability.
- **Dodge-roll** is available to all characters regardless of weapon
  loadout — the defensive option for two-handed Knight builds and Ninja
  loadouts that can't block.
- **Combat depth: pure skill**, no stamina bar. Attacks/blocks/dodges are
  unlimited; difficulty comes from enemy patterns, hitboxes, and timing —
  not a resource meter.
- **Loadout selection**: at the start of each level, pick **two** primary
  (melee) options and **one** secondary (ranged) option. The two melee
  options can be swapped mid-level via a button press; the ranged
  secondary is locked in for the whole level.
- **Ranged ammo**: limited, regenerates slowly over time (passive trickle).
  Pickups as a faster top-up are optional/TBD, not required for the
  system to work.

## Health / Lives / Checkpoints

- Lives-based: a limited pool of lives per level (count TBD, e.g. 3).
  Losing a life respawns you at the last checkpoint; running out of lives
  restarts the level.
- Checkpoints: 1 per level for standard levels, 2 for extra-long levels —
  roughly at the halfway point(s).
- Co-op: exact life-sharing/revive rules between the two players not yet
  decided (open item below).

## Levels (first playable vertical slice — 4 levels)

A visual arc where each level teases the next:

1. **Feudal Japan/China exterior** — traditional aesthetic, a giant temple
   visible in the background (parallax).
2. **Inside the temple** — large golden statues as set dressing/possible
   environmental hazards or boss elements.
3. **Mountainous region with a climbable waterfall** — platforms are rock
   outcroppings jutting from the waterfall; level goes *upward* rather than
   left-to-right. A castle is visible in the distance from the top.
4. **Inside the castle** — final level of the slice.

Enemies throughout are demons — some humanoid, some creature-like. Boss
fights include giants that are partly part of the environment (e.g. a boss
built into the temple or castle architecture). Specific enemy/boss rosters
are curated by the project owner directly, not invented ad hoc.

## Progression

- Weapon/gear unlocks only — no numeric stat-grinding (no RPG-style stat
  points). Power growth comes from unlocking new weapon options across the
  primary/secondary lists above.

## Tooling

- Engine: Godot 4
- Art: sprites/backgrounds via Pixellabs.ai
- Music: industrial metal instrumental tracks via Suno
- Team: ~4 friends contributing code, all using Claude

## Open Items

- Exact life-pool size per level, and whether co-op players share a life
  pool or have independent lives with revive-on-death mechanics.
- Specific enemy roster and boss designs per level (owner to curate).
- Ammo pickup mechanics as a supplement to passive regen (optional, TBD).
- Kimono Girl melee delivery-mode flavor, balance pass, and numeric tuning
  (see above).
- Repo/engine scaffolding (Godot 4 project skeleton) and a CLAUDE.md for
  contributor consistency — planned once the design is further along.
