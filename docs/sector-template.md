# The Sector Template

Agriculture is the pilot sector, built to full depth first; this document
is the pattern extracted from that work. Every other sector starts as a
skeleton with the same shape and deepens by following these steps.

## What every sector has (the skeleton)

```
schemas/sectors/<sector>/
├── <org_subtype>.yaml      # extends kelston.core.organization
├── <signature_entity>.yaml # the sector's emblematic thing (often extends place)
├── <record>.yaml           # extends kelston.core.civic_record
└── roles.yaml              # taxonomy data: industries + roles
```

- **Org subtype** (agriculture: `farm`): inherits name/sector/industry/
  realm/operating_cycle, adds what the sector genuinely tracks about its
  organizations. Because it *extends* organization, every employment and
  registry query already understands it.
- **Signature entity** (agriculture: `growing_plot`): the unit the sector's
  daily records hang off. If it has a location, extend `kelston.core.place`
  and the realm/tier machinery comes free.
- **Record type** (agriculture: `harvest_record`): extends
  `kelston.core.civic_record`, so the sector's events join the town-wide
  event spine (`recorded_at`, `recorded_by`) automatically.
- **roles.yaml**: industries and roles as *instances* of
  `kelston.core.industry` / `kelston.core.role`. Capability requirements
  are honest: a role demands `flight` only when the work happens in the air.

## How agriculture deepened (the roadmap for sector #2)

1. **Trace the sector's spine as entities**: farm -> growing_plot ->
   planting -> harvest_record -> market_lot -> distribution_run, plus the
   reference registers (crop_variety) and crafted goods (food_product).
   Each entity is the answer to "what does this sector make records *about*?"
2. **Factor shared categories into vocabularies** (soil_class, crop_kind,
   growing_method, produce_grade, drainage_class). If two schemas want the
   same category, it is a vocabulary, full stop.
3. **Make species traits structural** where the sector touches them:
   submerged plots require semi-aquatic stewards (constraint + rule);
   pollination roles require flight; the night markets require night_work.
4. **Write the constraints you would otherwise enforce by meeting**:
   method_suits_variety, lot_offers_exactly_one_source. Declarative first,
   one python rule when the logic truly needs it.
5. **Add a generator stage** (`kelston/generate/stages/<sector>.py`) that
   draws only from upstream stages' id pools, with its own named RNG.
6. **Register everything**: `kelston registry bump` per new standard;
   `kelston validate --all` green; queries in the cookbook.

## Rules of altitude

- An entity lives in **core** only if 2+ sectors must reference it by id.
- Sector schemas may reference core entities and their own sector's
  schemas - never another sector's. (Cross-sector links go through core:
  agriculture's distribution runs reference a *mobility organization*, not
  a mobility-internal schema.)
- New vocabularies belong to the town (`schemas/vocabularies/`), not the
  sector directory - the next sector may want them.
