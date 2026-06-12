"""SiteData: everything the portal pages need, computed once.

All statistics aggregate over the committed seed-42 fixtures via the same
Store the validator uses - the website shows the town as it provably is.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field

import yaml

from kelston import paths
from kelston.ksl.loader import Catalog, load_catalog
from kelston.ksl.validator import Store
from kelston.registry.manifest import load_manifest

CITIZEN = "kelston.core.citizen"
DWELLING = "kelston.core.dwelling"
ORGANIZATION = "kelston.core.organization"
FARM = "kelston.agriculture.farm"
HARVEST = "kelston.agriculture.harvest_record"
PLANTING = "kelston.agriculture.planting"
PLOT = "kelston.agriculture.growing_plot"
APPOINTMENT = "kelston.core.appointment"
MARKET_LOT = "kelston.agriculture.market_lot"


@dataclass
class SiteData:
    catalog: Catalog
    manifest: dict
    store: Store
    generation: dict
    realms: list[dict] = field(default_factory=list)
    species_by_id: dict[str, dict] = field(default_factory=dict)
    used_by: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def load(cls) -> "SiteData":
        if not paths.FIXTURES_DIR.exists():
            raise FileNotFoundError("data/fixtures/ missing - run `kelston generate` first")
        if not paths.MANIFEST.exists():
            raise FileNotFoundError("registry/manifest.yaml missing - run `kelston registry init`")
        catalog = load_catalog()
        store = Store.from_fixture_dir(paths.FIXTURES_DIR)
        generation_path = paths.FIXTURES_DIR / "generation.yaml"
        generation = (
            yaml.safe_load(generation_path.read_text(encoding="utf-8"))
            if generation_path.exists()
            else {"seed": 42, "population": 5000}
        )
        data = cls(
            catalog=catalog,
            manifest=load_manifest(),
            store=store,
            generation=generation,
        )
        data.realms = sorted(
            store.by_schema["kelston.core.realm"], key=lambda r: r["realm_code"]
        )
        data.species_by_id = {
            s["id"]: s for s in store.by_schema["kelston.core.species_profile"]
        }
        data.used_by = data._invert_dependencies()
        return data

    # ---- shared helpers ----------------------------------------------------

    def _invert_dependencies(self) -> dict[str, list[str]]:
        inverted: dict[str, list[str]] = defaultdict(list)
        for name, entry in self.manifest.get("schemas", {}).items():
            for requirement in entry.get("depends_on", []):
                target = requirement.split("@", 1)[0]
                inverted[target].append(name)
        return {k: sorted(v) for k, v in inverted.items()}

    @property
    def sectors(self) -> list[dict]:
        return self.catalog.vocabularies["kelston.vocab.sector"].terms

    def vocab_order(self, vocab_name: str) -> list[str]:
        return self.catalog.vocabularies[vocab_name].codes

    def vocab_label(self, vocab_name: str, code: str) -> str:
        for term in self.catalog.vocabularies[vocab_name].terms:
            if term["code"] == code:
                return term.get("label", code)
        return code

    def schemas_of_sector(self, sector_code: str) -> list:
        return sorted(
            (
                s
                for s in self.catalog.schemas.values()
                if s.name.split(".")[1] == sector_code
            ),
            key=lambda s: s.name,
        )

    def harvest_realm(self, harvest: dict) -> str:
        planting = self.store.by_id[harvest["planting"]]
        plot = self.store.by_id[planting["plot"]]
        return plot["realm"]

    def org_sector(self, org_id: str) -> str:
        return self.store.by_id[org_id]["sector"]

    # ---- aggregates --------------------------------------------------------

    def town_totals(self) -> dict:
        counts = {name: len(rows) for name, rows in self.store.by_schema.items()}
        return {
            "citizens": counts.get(CITIZEN, 0),
            "households": counts.get("kelston.core.household", 0),
            "dwellings": counts.get(DWELLING, 0),
            "organizations": counts.get(ORGANIZATION, 0) + counts.get(FARM, 0),
            "species": counts.get("kelston.core.species_profile", 0),
            "records": len(self.store.by_id),
            "schemas": len(self.catalog.schemas),
            "vocabularies": len(self.catalog.vocabularies),
            "sectors": len(self.sectors),
            "appointments": counts.get(APPOINTMENT, 0),
            "harvest_mass": round(
                sum(h["yield_mass"] for h in self.store.by_schema[HARVEST])
            ),
        }

    def population_by_realm(self) -> list[tuple[str, float]]:
        counts = Counter(c["realm"] for c in self.store.by_schema[CITIZEN])
        return [(r["name"], counts.get(r["id"], 0)) for r in self.realms]

    def realm_stats(self, realm: dict) -> dict:
        realm_id = realm["id"]
        citizens = [c for c in self.store.by_schema[CITIZEN] if c["realm"] == realm_id]
        dwellings = [d for d in self.store.by_schema[DWELLING] if d["realm"] == realm_id]
        organizations = [
            o
            for o in self.store.by_schema[ORGANIZATION] + self.store.by_schema[FARM]
            if o["realm"] == realm_id
        ]
        farms = [f for f in self.store.by_schema[FARM] if f["realm"] == realm_id]
        species_of = lambda c: self.species_by_id[c["species"]]  # noqa: E731

        class_mix = Counter(species_of(c)["animal_class"] for c in citizens)
        top_species = Counter(species_of(c)["common_name"] for c in citizens).most_common(5)
        shift_mix = Counter(c["active_hours_preference"] for c in citizens)
        tier_mix = Counter(d["vertical_tier"] for d in dwellings)
        climate_mix = Counter(d["climate_provision"] for d in dwellings)
        org_sectors = Counter(o["sector"] for o in organizations).most_common(6)
        harvest_mass = round(
            sum(
                h["yield_mass"]
                for h in self.store.by_schema[HARVEST]
                if self.harvest_realm(h) == realm_id
            )
        )
        shift_order = self.vocab_order("kelston.vocab.shift_band")
        tier_order = self.vocab_order("kelston.vocab.vertical_tier")
        return {
            "population": len(citizens),
            "households": len(
                {c["household"] for c in citizens}
            ),
            "organizations": len(organizations),
            "farms": len(farms),
            "growing_area": round(sum(f["total_growing_area"] for f in farms)),
            "harvest_mass": harvest_mass,
            "class_mix": [
                (cls.capitalize() + "s", class_mix[cls])
                for cls in ("mammal", "reptile", "bird")
                if class_mix.get(cls)
            ],
            "top_species": [(name, n) for name, n in top_species],
            "shift_mix": [
                (self.vocab_label("kelston.vocab.shift_band", b), shift_mix[b])
                for b in shift_order
                if shift_mix.get(b)
            ],
            "tier_mix": [
                (self.vocab_label("kelston.vocab.vertical_tier", t), tier_mix[t])
                for t in tier_order
                if tier_mix.get(t)
            ],
            "climate_mix": [
                (self.vocab_label("kelston.vocab.climate_provision", c), n)
                for c, n in climate_mix.most_common()
            ],
            "org_sectors": [
                (self.vocab_label("kelston.vocab.sector", s), n) for s, n in org_sectors
            ],
        }

    def sector_stats(self, sector_code: str) -> dict:
        industries = sorted(
            (
                i
                for i in self.store.by_schema["kelston.core.industry"]
                if i["sector"] == sector_code
            ),
            key=lambda i: i["id"],
        )
        industry_ids = {i["id"] for i in industries}
        roles = sorted(
            (
                r
                for r in self.store.by_schema["kelston.core.role"]
                if r["industry"] in industry_ids
            ),
            key=lambda r: r["id"],
        )
        roles_by_industry: dict[str, list[dict]] = defaultdict(list)
        for role in roles:
            roles_by_industry[role["industry"]].append(role)
        organizations = [
            o
            for o in self.store.by_schema[ORGANIZATION] + self.store.by_schema[FARM]
            if o["sector"] == sector_code
        ]
        appointments = sum(
            1
            for a in self.store.by_schema[APPOINTMENT]
            if self.org_sector(a["organization"]) == sector_code
        )
        return {
            "industries": industries,
            "roles_by_industry": roles_by_industry,
            "organizations": len(organizations),
            "appointments": appointments,
            "role_count": len(roles),
        }

    def dashboard_stats(self) -> dict:
        store, species = self.store, self.species_by_id
        citizens = store.by_schema[CITIZEN]
        realm_name = {r["id"]: r["name"] for r in self.realms}

        class_by_realm = defaultdict(Counter)
        for c in citizens:
            class_by_realm[c["realm"]][species[c["species"]]["animal_class"]] += 1

        size_order = self.vocab_order("kelston.vocab.size_class")
        size_mix = Counter(species[c["species"]]["size_class"] for c in citizens)

        shift_order = self.vocab_order("kelston.vocab.shift_band")
        shift_label = lambda b: self.vocab_label("kelston.vocab.shift_band", b)  # noqa: E731
        residents_by_band = Counter(c["active_hours_preference"] for c in citizens)
        worked_bands = Counter(a["shift_band"] for a in store.by_schema[APPOINTMENT])

        appointments_by_sector = Counter(
            self.org_sector(a["organization"]) for a in store.by_schema[APPOINTMENT]
        )

        harvest_by_realm = Counter()
        for h in store.by_schema[HARVEST]:
            harvest_by_realm[self.harvest_realm(h)] += h["yield_mass"]
        grade_order = self.vocab_order("kelston.vocab.produce_grade")
        harvest_by_grade = Counter()
        for h in store.by_schema[HARVEST]:
            harvest_by_grade[h["grade"]] += h["yield_mass"]

        climate_mix = Counter(
            d["climate_provision"] for d in store.by_schema[DWELLING]
        )
        lot_mass_by_realm = Counter()
        for lot in store.by_schema[MARKET_LOT]:
            lot_mass_by_realm[lot["market_realm"]] += lot["lot_mass"]

        return {
            "population_by_realm": self.population_by_realm(),
            "class_by_realm": [
                (
                    realm_name[r["id"]],
                    {
                        cls.capitalize() + "s": class_by_realm[r["id"]].get(cls, 0)
                        for cls in ("mammal", "reptile", "bird")
                    },
                )
                for r in self.realms
            ],
            "class_series": ["Mammals", "Reptiles", "Birds"],
            "size_mix": [
                (self.vocab_label("kelston.vocab.size_class", s), size_mix.get(s, 0))
                for s in size_order
            ],
            "residents_by_band": [
                (shift_label(b), residents_by_band.get(b, 0)) for b in shift_order
            ],
            "worked_bands": [
                (shift_label(b), worked_bands.get(b, 0)) for b in shift_order
            ],
            "appointments_by_sector": sorted(
                (
                    (self.vocab_label("kelston.vocab.sector", t["code"]),
                     appointments_by_sector.get(t["code"], 0))
                    for t in self.sectors
                ),
                key=lambda pair: -pair[1],
            ),
            "harvest_by_realm": [
                (r["name"], round(harvest_by_realm.get(r["id"], 0))) for r in self.realms
            ],
            "harvest_by_grade": [
                (self.vocab_label("kelston.vocab.produce_grade", g),
                 round(harvest_by_grade.get(g, 0)))
                for g in grade_order
            ],
            "climate_mix": [
                (self.vocab_label("kelston.vocab.climate_provision", c), n)
                for c, n in climate_mix.most_common()
            ],
            "lot_mass_by_realm": [
                (r["name"], round(lot_mass_by_realm.get(r["id"], 0)))
                for r in self.realms
            ],
        }
