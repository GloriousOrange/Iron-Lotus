# Iron Lotus (working title)

A dark, gritty 2D side-scrolling action platformer with local couch co-op.
Built in Godot 4.

This README is the living game design document. It will be updated as the
design evolves — nothing here is final until we start locking systems down
for implementation.

## Status

**Early implementation.** This README is still the living design
reference (4 friends + the project owner, all collaborating via Claude),
but a first-pass Godot 4 project now exists: Kageharu (Ninja) is playable
with a placeholder moveset and a test Level 1 scene (parallax background,
a couple of humanoid/flying placeholder enemies). Everything else in this
doc is still design-only until it gets built the same way.

## Lore

**The House of the Iron Lotus** is a clan dedicated to fighting the
Demonic Scourge — demons are spreading across the world, and the House is
one of the forces standing against them. (Likely the game's actual title.)
Members join it by very different paths:

- The **Ninja (Kageharu)** and the **Kimono Girl (Yukiko)** are a couple —
  professional thieves. Her elemental magic comes from a set of enchanted
  items the pair stole during a job. They were eventually captured by the
  authorities and given a choice: execution, or serve the Iron Lotus until
  death. They're conscripts, not volunteers.
- **Sir Garrick Voss (Knight)** and **Father Malachi (Priest)** come from a
  far-away land. They traveled East seeking the source of the Demonic
  Corruption and joined the House of the Iron Lotus voluntarily, out of
  purpose rather than punishment.
- **Trygger (Viking)** and **Astrid (Seidr Witch)** were warriors from the
  far northern mountains. Like Voss and Malachi, they came looking for
  the source of the Demonic uprising and joined the House of the Iron
  Lotus voluntarily.

This sets up a tonal contrast worth keeping in mind for writing/dialogue:
conscripted criminals fighting alongside true-believer crusaders (two of
the latter, from two different distant lands), all under the same banner.

## Pillars

- Dark, gritty tone. Industrial metal instrumental soundtrack (already
  produced via Suno).
- Visually inspired by *Abathor*: multi-layer parallax backgrounds (e.g.
  distant crashing waves scrolling slower than the walkable foreground).
- Hard but fair — Souls-adjacent difficulty via enemy patterns and precise
  play, not stat-checks.
- Local couch co-op, multiple very differently-controlled characters,
  organized as three pairs (skill fighter + spellcaster): Ninja
  (Kageharu)/Kimono Girl (Yukiko), Knight (Sir Garrick Voss)/Priest
  (Father Malachi), Viking (Trygger)/Seidr Witch (Astrid).
- Godot 4, PC-only for the initial build (no online netcode, no mobile).

## Characters

### Ninja — Kageharu
- Backstory: professional thief, partner of the Kimono Girl (see Lore
  above).
- Agile: wall-climb, slide, wall-jump, dodge-roll.
- Primary (melee) — pick **two** per level, swappable mid-level via button:
  **katana, double sais, staff, nun-chucks**.
- Secondary (ranged, limited ammo) — pick **one** per level, locked for the
  whole level: **ninja stars, giant ninja stars, throwing spikes**.
- Blocking: only available with **staff** or **katana**. No blocking with
  nun-chucks or sais — those loadouts rely on the universal dodge-roll
  instead.
- Ranged use: stuns for ~1s, or kills light enemies outright.

### Viking — Trygger
- Backstory: warrior from the far northern mountains, partner of the Seidr
  Witch; came seeking the source of the Demonic uprising and joined the
  House of the Iron Lotus voluntarily (see Lore above).
- Primary (melee) — pick **two** per level, swappable mid-level via button:
  **double axes, spear, sword and shield, two-handed maul**.
- Secondary (ranged, limited ammo) — pick **one** per level, locked for the
  whole level: **throwing axes, heavy rock, throwing knives**.
- Blocking/defense specifics not yet defined (open item below) — presumably
  sword+shield offers a block like the Knight's, with dodge-roll as the
  universal fallback for the other loadouts.

### Knight — Sir Garrick Voss
- Backstory: traveled from a far-away land with the Priest, seeking the
  source of the Demonic Corruption; joined the House of the Iron Lotus
  voluntarily (see Lore above).
- Armored, no wall-climb, but can wall-jump. Dodge-roll available
  regardless of loadout.
- Primary (melee) — pick **two** per level, swappable mid-level via button:
  - One-handed + shield: **sword, mace, flail** (each paired with a shield)
  - Two-handed (no shield): **battle axe** (maul reassigned to the Viking)
- Secondary (ranged, limited ammo) — pick **one** per level, locked for the
  whole level: **bow and arrows, crossbow, throwing axes**.
- Shield block is aimable in three directions via the block button: held
  forward (standard block), raised overhead (anti-aerial-attack block), or
  angled diagonally. Only available on one-handed+shield loadouts.

### Kimono Girl — Yukiko (elemental spellcaster)
- Backstory: professional thief, partner of the Ninja (see Lore above). Her
  magic comes from enchanted items stolen during a heist — possibly the
  fans themselves.
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
| Water+Water | Water-jet burst, short knockback | Grows a bubble while held; releasing launches it to slowly seek out an enemy and explode on impact — bigger bubble (longer hold) = more damage | Continuous water stream (pushback; douses fire hazards) |
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

### Priest — Father Malachi (Aspect-based spellcaster)
- Backstory: traveled from a far-away land with the Knight, seeking the
  source of the Demonic Corruption; joined the House of the Iron Lotus
  voluntarily (see Lore above).
- Melee: **Aspergillum** (a holy-water sprinkler) — Aspect-infused, single
  loadout for the whole level, cooldown-based (infinite uses, stronger
  spells → longer cooldown). Uses the same combo matrix as the books
  (below), configured independently.
- Ranged: **two books** — a **Holy Book** and a **Necronomicon** — in
  place of the Kimono Girl's fans. Each independently configured, swappable
  mid-level via a button press, drawing from a shared regenerating **mana
  pool**.
- **Spell-building system**: mirrors the Kimono Girl's exactly, but with
  different vocabulary — select two **Aspects** (repeats allowed) from
  **Body, Mind, Spirit, Blood**, plus a **Mode**: **Order**, **Chaos**, or
  **Balance**. Aspect order never matters (Mind+Body == Body+Mind).

#### Aspect Combo Matrix (complete: 10 pairs x 3 modes = 30 spells)

**Pure pairs:**

| Aspect | Order | Chaos | Balance |
|---|---|---|---|
| Mind+Mind | Telekinetic blast that pushes enemies — extra damage if pushed into a wall or another enemy | Telekinetic explosion damaging everyone on screen, including the Priest himself | Aura granting increased attack speed to self and teammates/summons |
| Body+Body | Hardened Flesh — temporary armor | Become muscular, deliver powerful punches at a health cost | Slow health regeneration |
| Spirit+Spirit | Spirit Ward — temporary shield | Soul Sunder — projectile that silences magic users (can't cast for a duration) | Soul Tether — whichever player has lower health heals up to the other player's level over time |
| Blood+Blood | Blood Sabre — a red saber that heals the user a little on each hit landed on a bleeding enemy (some enemies, like golems and skeletons, don't bleed) | Corpse Explosion — a fallen enemy explodes, damaging nearby enemies | Red aura that heals allies and harms enemies it touches |

**Mixed pairs:**

Aspect order never matters (Mind+Body == Body+Mind).

| Aspects | Order | Chaos | Balance |
|---|---|---|---|
| Mind+Body | Dominion — take control of a standard enemy (won't work on powerful enemies) | Mind Fever — target enemy becomes 2x speed and attacks allies or foes at random | Self-use only: trades the Priest's own health/mana, whichever is higher moving to whichever is lower, until equal |
| Mind+Spirit | Revelation — a hovering orb that sheds light and highlights enemy weak points | Aura granting allies random temporary boosts (higher jumps, faster attacks, more damage, or slow HP/mana regen) | Clarity Aura — reduces cooldowns for the whole team |
| Mind+Blood | Blood Sigil — a trap that damages and burns the mana of a foe caught in it for a duration | Blood Star — a red star projectile that steals health | Contagious Suffering — a dark aura that makes affected enemies share a single health pool |
| Body+Spirit | Ascension — temporary flight | Summon a Winged Gargoyle to fight enemies | Slow health and mana regeneration |
| Body+Blood | Blood Armor — red orbs spin around you, absorbing hits and popping when struck | Blood Whip — a whip of blood from the hand, high damage at a health cost | Fully heal a downed teammate |
| Spirit+Blood | Summon a Ghost to fight enemies | Summon a Zombie to fight enemies | Drain enemy life into orbs that player characters can pick up to heal from |

The same matrix drives both the Aspergillum (melee) and the two books, but
all three are configured independently at level start (3 separate loadout
choices: melee spell, Holy Book spell, Necronomicon spell). Melee is
cooldown-based (per-spell cooldown, infinite uses); books draw from the
shared mana pool.

**Resolved:** the Holy Book and Necronomicon aren't a gameplay restriction —
they're a visual "prop swap." Whichever book matches the spell being cast
is the one the Priest pulls out automatically: the blue Holy Book for holy
spells, the black Necronomicon for dark spells. (Likely maps to Order =
holy/blue, Chaos = dark/black; Balance's book is still open — could go
either way per spell, or have its own visual treatment.)

**Still open:**
- Which book Balance-mode spells pull (context-dependent per spell, a
  dedicated "neutral" treatment, or always defaults to one book).
- Melee-specific (Aspergillum) meaning of Order/Chaos/Balance where effects
  above were written with book/ranged delivery in mind.
- Numeric tuning (damage, durations, mana cost/cooldown per mode, shared
  health-pool mechanics for Contagious Suffering, etc.) — concept/effect
  level only for now.

### Seidr Witch — Astrid (Norse spellcaster)
- Backstory: warrior from the far northern mountains, partner of the
  Viking; came seeking the source of the Demonic uprising and joined the
  House of the Iron Lotus voluntarily (see Lore above).
- Melee: **Seidr Staff** — cosmetic variants under discussion (crescent-moon
  staff, gemmed wooden staff, or crystal-tipped metal rod; TBD which, same
  open question as the Kimono Girl's chopsticks/hairpin). Aspect-infused,
  single loadout for the whole level, cooldown-based (infinite uses,
  stronger spells → longer cooldown). Uses the same combo matrix below.
- Casting: **single casting method**, no dual-item split like the fans/
  books — unlike Kimono Girl and Priest, she has only **one** configured
  spell for her ranged/cast slot (not two), presumably drawing from a
  regenerating mana pool like the others (open item: confirm mana vs. some
  other resource).
- **Spell-building system**: select two **Aspects** (repeats allowed) from
  **Storm, Beast, Poison, Berserk**, plus a **Mode**: **Shout**, **Rune**,
  or **Alchemy**. Aspect order never matters.

#### Aspect Combo Matrix (complete: 10 pairs x 3 modes = 30 spells)

**Pure pairs:**

| Aspect | Shout | Rune | Alchemy |
|---|---|---|---|
| Storm+Storm | Thunder Scream — a lightning bolt shoots from the mouth, knocking enemies back and damaging them | Thor's Rune — a placed rune attracts lightning strikes to its location | Storm Vial — a storm cloud follows the player, striking lightning at her feet at random times, hitting any enemy in between |
| Beast+Beast | Primal Howl — summons two wolves to fight enemies | Murder of Crows — a placed rune draws a crow swarm that causes damage | Beast Blood Elixir — a drinkable potion that temporarily turns her into a werewolf |
| Poison+Poison | Venom Spit — spits black poison onto an enemy, draining health slowly | Rune of Wither — a placed rune damages enemies who stand near it | Plague Brew — a throwable vial that breaks on impact, leaving a puddle and a poisonous gas cloud that poisons enemies who touch it |
| Berserk+Berserk | War Scream — boosts damage for the whole team | Frenzy Rune — a placed rune gives enemies who touch it double attack speed but double damage taken | Drinkable potion that doubles attack speed for a duration |

**Mixed pairs:**

Aspect order never matters (Storm+Poison == Poison+Storm).

| Aspects | Shout | Rune | Alchemy |
|---|---|---|---|
| Storm+Poison | Sunder Voice — weakens and breaks the armor of the nearest enemy | Serpent Rune — summons a venomous snake that strikes and badly poisons anyone who comes near | Releases poisonous clouds that rain acid, destroying the armor of any enemy on screen |
| Storm+Berserk | A violent thunderstorm that pushes enemies in random directions and damages them | A placed rune starts a tornado that tosses enemies upward and damages them | Stormfury Elixir — a drinkable potion that adds lightning damage to self and allies |
| Beast+Poison | Summons a swarm of bees that damage and poison multiple enemies | A placed rune summons a swarm of poisonous bats at that location | Plague Beast Tonic — a drinkable potion that turns her into a lizard person that inflicts poison on hit |
| Beast+Berserk | Primal Rage — summons a Cave Bear to fight for her | Rune of Rage — a placed rune gives allies standing in it a damage and attack-speed increase | A drinkable potion that turns her into a huge eagle |
| Poison+Berserk | Vile Shriek — poisons allies but grants them temporary increased movement and attack speed | A placed rune that badly poisons enemies who touch it, but also gives them increased attack and movement speed (risk/reward trap) | A drinkable potion that turns her into a venom-spitting velociraptor |

**Still open:**
- Confirm resource for her single cast slot (mana pool like the others, or
  something distinct).
- Melee-specific (Seidr Staff) meaning of Shout/Rune/Alchemy where effects
  above were written with ranged/cast delivery in mind.
- Seidr Staff's final cosmetic form (crescent moon / gemmed wood / crystal
  rod) and whether it's a real choice or flavor-only.
- Viking/Seidr Witch backstory and how it parallels or contrasts the other
  two pairs (conscripts vs. volunteers).
- Numeric tuning (damage, DOT/poison ticks, durations, mana cost/cooldown
  per mode) — concept/effect level only for now.

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
  (melee) options and **one** secondary (ranged) option. Both melee
  options are simultaneously available in-level via two separate attack
  buttons (see Controls below) — no swap button/animation needed. The
  ranged secondary is locked in for the whole level.
- **Blocking gate**: a character can block if *either* of their two
  equipped melee options supports blocking (e.g. loading in a katana AND
  nun-chucks still lets the Ninja block, even mid-swing with the
  nun-chucks) — blocking isn't tied to "whichever weapon you swung last."
- **Ranged ammo**: limited, regenerates slowly over time (passive trickle).
  Pickups as a faster top-up are optional/TBD, not required for the
  system to work.

### Controls (generic gamepad)

One control scheme across all six characters, so switching characters in
co-op doesn't mean relearning buttons:

| Button | Action |
|---|---|
| A (bottom face) | Jump |
| X (left face) | Attack 1 |
| Y (top face) | Attack 2 |
| B (right face) | Attack 3 |
| Left shoulder | Block (only does anything if the loadout allows it) |
| Right shoulder | Dodge-roll |
| Start | Pause |

Attack 1/2/3 map differently by character archetype, but always cover "the
two equipped melee options + the ranged/secondary":
- **Skill fighters** (Ninja, Knight, Viking): Attack 1/2 = the two equipped
  melee weapons, Attack 3 = the ranged throw.
- **Casters** (Kimono Girl, Priest, Seidr Witch): Attack 1 = the melee
  weapon/relic, Attack 2/3 = the two configured secondary items (fans/
  books). The Seidr Witch currently has only one cast slot (see her open
  items), so her Attack 3 mapping is still open.

Keyboard equivalents exist for testing (WASD/arrows move, Space jump,
J/K/L = Attack 1/2/3, Shift block, Ctrl dodge, Esc pause) but the gamepad
scheme above is the primary target.

## Health / Lives / Checkpoints

- Lives-based: a limited pool of lives per level (count TBD, e.g. 3).
  Losing a life respawns you at the last checkpoint; running out of lives
  restarts the level.
- Checkpoints: 1 per level for standard levels, 2 for extra-long levels —
  roughly at the halfway point(s).
- Co-op: exact life-sharing/revive rules between the two players not yet
  decided (open item below).

## Levels

Levels so far seem to be forming into per-pair chapters/arcs rather than
one single shared list — worth confirming that structure explicitly (open
item below), but tracking them that way for now.

### Feudal East arc (Ninja / Kimono Girl?) — first playable vertical slice, 4 levels

A visual arc where each level teases the next:

1. **Feudal Japan/China exterior** — traditional aesthetic, a giant temple
   visible in the background (parallax).
2. **Inside the temple** — large golden statues as set dressing/possible
   environmental hazards or boss elements.
3. **Mountainous region with a climbable waterfall** — platforms are rock
   outcroppings jutting from the waterfall; level goes *upward* rather than
   left-to-right. A castle is visible in the distance from the top.
4. **Inside the castle** — final level of the slice.

### Norse arc (Viking / Seidr Witch) — 2 levels so far

1. **Beach**.
2. **A large ship, under attack by sea creatures.**

Enemies throughout are demons — some humanoid, some creature-like (plus,
per the Norse arc, sea creatures). Boss fights include giants that are
partly part of the environment (e.g. a boss built into the temple or
castle architecture). Specific enemy/boss rosters are curated by the
project owner directly, not invented ad hoc.

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
- Confirm whether levels are organized as per-pair chapters/arcs (as
  currently tracked) and which pair the Feudal East arc actually belongs
  to — assumed Ninja/Kimono Girl by aesthetic fit, never explicitly stated.
- Ammo pickup mechanics as a supplement to passive regen (optional, TBD).
- Kimono Girl melee delivery-mode flavor, balance pass, and numeric tuning
  (see above).
- Priest melee (Aspergillum) delivery-mode flavor, numeric tuning, and
  which book Balance-mode spells pull (see above).
- Seidr Witch melee/cast-resource/cosmetic details and Viking/Seidr Witch
  backstory (see above); Viking's blocking/defense specifics (sword+shield
  presumed to block like the Knight, unconfirmed).
- Repo/engine scaffolding (Godot 4 project skeleton) and a CLAUDE.md for
  contributor consistency — planned once the design is further along.
