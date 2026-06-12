# The Kelston World Bible

Kelston is a town of animal citizens - mammals, reptiles, and birds -
built where seven biomes meet. The tone sits between contemporary and
solarpunk: the apex of what we have, maybe a tiny bit further. No one is
asked to fight their own biology; the town's systems are built so that a
shrew, a crocodile, and a snowy owl get the same quality of civic life
through the same standards.

Diet and predation are deliberately out of frame. Kelston's tables are set
from its farms, and the question is left where the storybooks leave it.

## The seven realms

| Code | Name | Biome | Known for |
|---|---|---|---|
| `commons` | The Commons | meadow & river junction | the registry, the assembly, the grand market |
| `evergreen` | The Evergreen | temperate forest | timbercraft, orchards, trunk-and-burrow streets |
| `canopy` | The Canopy | jungle | vertical living, agroforestry, rope-ways |
| `frostlands` | The Frostlands | tundra | the glass quarter's greenhouse rows |
| `shorelines` | The Shorelines | coast & estuary | harbors, paddies, kelp lines, stilt streets |
| `highlands` | The Highlands | mountains | terraces, aeries, the observatory |
| `drylands` | The Drylands | desert | drip-fed groves, basking grounds, night markets |

Every realm is mixed-species - affinity weights who tends to settle where,
never who may. The Drylands runs on a dusk-to-dawn rhythm; its markets wake
when the Commons sleeps, and the town's scheduling standards (shift bands)
treat that as normal, not exceptional.

## How species traits shape the town (structurally)

These are data, not flavor - every one is a field in
[`kelston.core.species_profile`](../schemas/core/species_profile.yaml)
that other standards check against:

- **size_class** (ordered: tiny -> grand): housing clearance, transit
  seating, furniture and tool standards. A dwelling's `clearance_class >=`
  every occupant's `size_class` is a validated constraint.
- **activity_cycle**: maps to the four shift bands (dawn/day/dusk/night).
  Appointments, transit runs, and operating cycles all speak in bands, so
  nocturnal citizens hold ordinary jobs at ordinary hours - theirs.
- **locomotion** (multi-valued): flighted citizens get aerial lanes, landing
  perches, and roles that genuinely require flight; semi-aquatic citizens
  get swim-ways, water boarding, and homes with swim-in access; fossorial
  citizens get the burrow tier.
- **thermoregulation**: ectotherms (Kelston's reptiles) are entitled to
  basking provisions at home and at work - checkable, because provisions
  are data.
- **lifespan_band** (brief -> venerable): education pacing, care services,
  and civic adulthood are paced per band, so a brief-band mouse and a
  venerable-band tortoise each get a whole life's worth of services at
  their own tempo.

## The vertical town

Kelston builds in five tiers - burrow, ground, canopy, rooftop, submerged -
and the tier is a field on every place. The Shorelines is the only realm
with submerged front rooms; the Canopy's front doors average forty meters
up; the Commons stacks burrow workshops under tower flats.

## Civic machinery

The kelmark is the unit of account. The civic calendar is the ordinary
12-month calendar - Kelston idealizes its data, not its astronomy. The
registry of record lives in the Commons, and the **standards office**
(governance sector) stewards the very schemas in this repository; the
town's data standards are, in-world, a public utility maintained like the
waterworks.

## Naming

Citizens carry a given name and a family name (`world/naming/names.yaml`).
Family names run earthy for mammals (Thornpaw, Mossburrow), sun-and-stone
for reptiles (Sunscale, Duneshade), wind-and-feather for birds
(Featherlight, Galecrest), with a shared pool (Kelbrook, Wintermere) that
mixed households often choose.
