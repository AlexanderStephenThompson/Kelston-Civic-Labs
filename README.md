# Kelston Civic Labs

A thought experiment made executable: **what would a society's information
systems look like if they were designed well from the start?**

Kelston is a town of animal citizens - mammals, reptiles, and birds -
spread across seven biome realms. Its premise: the town defined its
fields, industries, and roles up front, and everyone in an industry
follows the same semantic, intuitive data standards. So data cleaning
largely doesn't exist, and when a standard changes, every record in town
receives the update through one command - provably, with validation.

This repository is that town: the standards, the registry that versions
them, the tooling that enforces them, and a generated population of 5,000
citizens living inside them.

```
pip install -e .
kelston validate --all     # meta, registry, instances, determinism - all green
kelston generate --seed 42 # rebuild the town: fixtures + data/kelston.db
kelston upgrade            # walk legacy records through migrations, re-validate
kelston query "SELECT ..." # ask the town anything
kelston build-site         # render the civic portal; browse with
                           #   python -m http.server -d site
```

**The civic portal** - a 136-page static website generated from the town's
real records: realm pages with live statistics, the full standards registry
(every schema, vocabulary, and version history), and SVG civic dashboards.
No frameworks, no trackers; deploys to GitHub Pages from main.

## What's here

| | |
|---|---|
| `schemas/_meta/` | The Kelston Schema Language, described in itself |
| `schemas/core/` | The universal layer: citizen, household, dwelling, organization, role, the event spine |
| `schemas/vocabularies/` | 38 shared standards - species traits, units, shift bands, soils... |
| `schemas/sectors/` | All 17 sectors of town life, each with schemas + role taxonomy |
| `registry/` | The manifest (versions, checksums, dependencies, history), migrations, archives |
| `world/` | Lore as data: 7 realms, 58 species with structural traits, the seed register |
| `kelston/` | Python tooling: validator, registry, deterministic generator, SQLite emitter |
| `data/fixtures/` | The committed seed-42 town, 13,000+ records, diffable JSONL |
| `docs/` | The handbook (start with the KSL spec and the world bible) |

## The ideas, in one tour each

- **Semantic standards** - field names that read as sentences, mandatory
  descriptions, units declared in the schema, typed references. CI enforces
  all of it. -> [docs/ksl-spec.md](docs/ksl-spec.md)
- **Seamless updates** - semver per standard, mechanically classified
  diffs, declarative migrations, instances stamped with what they conform
  to. The repo ships a real worked example: growing_plot 1.2.0 -> 2.0.0,
  185 legacy records, zero failures. -> [docs/versioning.md](docs/versioning.md)
- **Species traits are structural** - size classes drive housing clearance,
  activity cycles drive shift scheduling, locomotion drives who stewards
  the submerged paddies (harbor seals and capybaras, as it happens),
  thermoregulation drives basking provisions. Constraints, not flavor.
  -> [docs/world-bible.md](docs/world-bible.md)
- **One sector perfected, sixteen to follow** - agriculture is built to
  full depth (farm -> plot -> planting -> harvest -> market lot ->
  distribution run) and the pattern is documented as a template.
  -> [docs/sector-template.md](docs/sector-template.md)
- **A town you can query** - -> [docs/query-cookbook.md](docs/query-cookbook.md)
- **An economy with a shape** - the Get / Make / Move taxonomy the town's
  industries are organized around, and a de-branded supply-chain reference
  behind it. Reference material rather than executable standards: it is
  what the sector schemas are modelled on.
  -> [docs/economy-mapping.md](docs/economy-mapping.md),
  [docs/logistics.md](docs/logistics.md)

## Why

Once the systems exist, the instances become a playground: simulations,
apps, policy what-ifs, new sectors, new towns. Kelston is the fixture for
every future experiment about how a society's information could work.
