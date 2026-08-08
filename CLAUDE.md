<!-- LINEAGE: layer=3 brand=kelston-chronicles hub=../_Assets/kelston-chronicles-AI-Hub -->

# Kelston Civic Labs — Reference for AI assistants

Python package (`kelston`), not a website or a 3D folder. It models Kelston's civic information
systems as executable, versioned data standards and generates a town of 5,000 citizens that
conforms to them.

**This is the only published repo in `World Building/`** — `AlexanderStephenThompson/Kelston-Civic-Labs`
on GitHub, one of the four GitHub-bound repos on the whole drive. Everything else in this tree is
deliberately local-only, so the usual "no remote is fine" rule does **not** apply here: work landing
on `main` is public.

## Canon relationship

The town modelled here is the same Kelston as `VR World/`, `Games/`, and `kelston-chronicles-site/`.
Lore lives in `world/lore/` **as data** — 7 realms, 58 species with structural traits — and
`docs/world-bible.md` is the prose statement. When the lore here and the brand hub's
`Project/lore/` disagree, they are describing one world and the disagreement is a bug: reconcile,
do not fork.

The distinguishing rule: **species traits are structural, not flavor.** Size class drives housing
clearance, activity cycle drives shift scheduling, locomotion drives who works the submerged
paddies, thermoregulation drives basking provisions. A change to a species trait is a change to
the town's logistics, so never adjust one as a cosmetic tweak.

## Layout

| Path | Holds |
|---|---|
| `schemas/_meta/` | the Kelston Schema Language, described in itself |
| `schemas/core/` | universal layer — citizen, household, dwelling, organization, role, event spine |
| `schemas/vocabularies/` | 38 shared standards (species traits, units, shift bands, soils) |
| `schemas/sectors/` | 17 sectors, each with schemas + role taxonomy; agriculture is the built-to-depth reference |
| `registry/` | the manifest — versions, checksums, dependencies, history, migrations, archives |
| `world/` | lore as data: realms, species, the seed register |
| `kelston/` | the tooling — `cli.py`, `registry/`, `rules/`, `generate/`, `db/`, `ksl/`, `site/` |
| `data/fixtures/` | the committed seed-42 town, 13,000+ records, diffable JSONL |
| `docs/` | the handbook — start with `ksl-spec.md` and `world-bible.md` |

## Working here

```bash
pip install -e .
kelston validate --all       # meta, registry, instances, determinism
kelston generate --seed 42   # rebuild fixtures + data/kelston.db
kelston upgrade              # walk legacy records through migrations, re-validate
kelston build-site           # render the civic portal
pytest                       # testpaths = tests
ruff check .                 # line-length 100, target py310
```

**`kelston validate --all` is the gate.** It checks the meta-schema, the registry, every instance,
and determinism. Run it before any commit — a schema edit that validates alone can still break the
registry's checksums or the generator's determinism.

**Generation is deterministic and that is load-bearing.** `--seed 42` must produce byte-identical
fixtures; the committed `data/fixtures/` is the proof and diffs are meant to be readable. If a
change makes the output differ without you intending it, the change is wrong — do not re-baseline
the fixtures to make a diff go away.

## Conventions

- **Schema changes are versioned, never edited in place.** Semver per standard, diffs mechanically
  classified, migrations declared, instances stamped with what they conform to. `growing_plot`
  1.2.0 → 2.0.0 across 185 legacy records is the worked example — follow its shape.
- **Field names read as sentences**, descriptions are mandatory, units are declared in the schema,
  references are typed. CI enforces this; see `docs/ksl-spec.md`.
- **Adding a sector?** `docs/sector-template.md` is the pattern, derived from agriculture.
- **The generated site is a build artifact** — edit templates in `kelston/site/`, never the output.
