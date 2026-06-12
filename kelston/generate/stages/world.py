"""Stage: load the authored world (realms, species, seed register, the
sector taxonomy) and lay out the town's parcels."""

from __future__ import annotations

import yaml

from kelston import paths
from kelston.generate.context import GenContext

# How many parcels each realm registers, tuned to a 5,000-citizen town.
PARCELS_PER_REALM = {
    "commons": 140,
    "evergreen": 90,
    "canopy": 70,
    "frostlands": 60,
    "shorelines": 90,
    "highlands": 70,
    "drylands": 80,
}

LAND_USE_WEIGHTS = [
    ("residential", 52),
    ("agricultural", 16),
    ("commercial", 10),
    ("civic", 6),
    ("industrial", 5),
    ("parkland", 7),
    ("mixed", 4),
]

AREA_BY_USE = {  # square meters, (low, high)
    "residential": (400, 3000),
    "agricultural": (3000, 40000),
    "commercial": (300, 2500),
    "civic": (500, 6000),
    "industrial": (1000, 12000),
    "parkland": (2000, 60000),
    "mixed": (400, 3000),
}


def load_world(ctx: GenContext) -> None:
    for path in (
        paths.WORLD_DIR / "realms.yaml",
        paths.WORLD_DIR / "species_roster.yaml",
        paths.WORLD_DIR / "crop_varieties.yaml",
    ):
        with open(path, encoding="utf-8") as handle:
            for instance in yaml.safe_load(handle):
                ctx.adopt(instance)
    for roles_path in sorted(paths.SECTORS_DIR.glob("*/roles.yaml")):
        with open(roles_path, encoding="utf-8") as handle:
            taxonomy = yaml.safe_load(handle)
        for industry in taxonomy.get("industries", []):
            ctx.adopt(industry)
        for role in taxonomy.get("roles", []):
            ctx.adopt(role)


def generate_parcels(ctx: GenContext) -> None:
    rng = ctx.rng("parcels")
    uses, weights = zip(*LAND_USE_WEIGHTS)
    for realm in ctx.all_of("kelston.core.realm"):
        for _ in range(PARCELS_PER_REALM[realm["realm_code"]]):
            land_use = rng.choices(uses, weights=weights)[0]
            low, high = AREA_BY_USE[land_use]
            tier_pool = realm.get("dominant_tiers") or ["ground"]
            ctx.add(
                "kelston.core.parcel",
                realm=realm["id"],
                land_use=land_use,
                area=round(rng.uniform(low, high)),
                vertical_tier=rng.choice(tier_pool) if rng.random() < 0.5 else "ground",
            )


def run(ctx: GenContext) -> None:
    load_world(ctx)
    generate_parcels(ctx)
