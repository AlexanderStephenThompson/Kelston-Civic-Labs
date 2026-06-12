"""Stage: the pilot sector at full depth - plots, plantings, harvests,
food products, market lots, and distribution runs."""

from __future__ import annotations

import datetime as dt
from collections import defaultdict

from kelston.generate.context import GenContext

SOILS_BY_REALM = {
    "commons": ["loam", "silt"],
    "evergreen": ["loam", "peat"],
    "canopy": ["loam", "volcanic"],
    "frostlands": ["loam", "peat"],
    "shorelines": ["clay", "peat"],
    "highlands": ["volcanic"],
    "drylands": ["sand", "loam"],
}

# Mirrors the 2.0.0 migration deriver, so legacy round-trips are exact.
DRAINAGE_BY_SOIL = {
    "sand": "free_draining",
    "volcanic": "free_draining",
    "clay": "water_holding",
    "peat": "water_holding",
    "substrate_water": "water_holding",
}

SUBMERGED_METHODS = {"paddy", "aquaponic"}
GRADE_WEIGHTS = [("seconds", 15), ("standard", 55), ("choice", 22), ("prime", 8)]
PRICE_BY_KIND = {
    "grain": (2, 5), "leaf_green": (3, 7), "root": (2, 6), "legume": (3, 7),
    "fruit": (4, 9), "berry": (6, 12), "nut": (7, 14), "gourd": (3, 6),
    "herb": (8, 16), "fungus": (6, 12), "kelp": (3, 6), "nectar_flower": (9, 18),
}


def run(ctx: GenContext) -> None:
    rng = ctx.rng("agriculture")
    realms = {r["id"]: r for r in ctx.all_of("kelston.core.realm")}
    varieties = ctx.all_of("kelston.agriculture.crop_variety")
    species_by_id = {s["id"]: s for s in ctx.all_of("kelston.core.species_profile")}
    citizens_by_id = {c["id"]: c for c in ctx.all_of("kelston.core.citizen")}

    farm_staff: dict[str, list[dict]] = defaultdict(list)
    for appointment in ctx.all_of("kelston.core.appointment"):
        farm_staff[appointment["organization"]].append(
            citizens_by_id[appointment["citizen"]]
        )

    harvests_by_farm: dict[str, list[dict]] = defaultdict(list)
    for farm in ctx.all_of("kelston.agriculture.farm"):
        realm = realms[farm["realm"]]
        plots = _plots_for_farm(ctx, rng, farm, realm, species_by_id, farm_staff[farm["id"]])
        for plot in plots:
            for planting in _plantings_for_plot(ctx, rng, plot, varieties, realm):
                harvests_by_farm[farm["id"]].extend(
                    _harvests(ctx, rng, plot, planting, varieties)
                )

    products = _food_products(ctx, rng)
    lots = _market_lots(ctx, rng, harvests_by_farm, products, realms)
    _distribution_runs(ctx, rng, lots, realms)


def _plots_for_farm(ctx, rng, farm, realm, species_by_id, staff):
    plots = []
    submerged_farm = any(m in SUBMERGED_METHODS for m in farm["primary_methods"])
    swimmers = [
        c for c in staff
        if "semi_aquatic" in species_by_id[c["species"]]["locomotion"]
    ]
    area_left = farm["total_growing_area"]
    for _ in range(rng.randint(3, 12)):
        if area_left < 200:
            break
        area = round(min(rng.uniform(150, 2500), area_left))
        area_left -= area
        submerged = submerged_farm and rng.random() < 0.7
        if submerged:
            soil = "substrate_water"
            steward = rng.choice(swimmers)["id"] if swimmers else None
            tier = "submerged"
        else:
            soil = rng.choice(SOILS_BY_REALM[realm["realm_code"]])
            steward = rng.choice(staff)["id"] if staff else None
            tier = (
                "rooftop"
                if "rooftop_garden" in farm["primary_methods"] and rng.random() < 0.35
                else "ground"
            )
        drainage = DRAINAGE_BY_SOIL.get(soil, "moderate")
        # Some loam plots carry the drainage the legacy 1.x soil codes implied.
        if soil == "loam":
            roll = rng.random()
            drainage = "water_holding" if roll < 0.2 else (
                "free_draining" if roll < 0.4 else "moderate"
            )
        plots.append(
            ctx.add(
                "kelston.agriculture.growing_plot",
                realm=realm["id"],
                vertical_tier=tier,
                farm=farm["id"],
                area=area,
                soil_class=soil,
                drainage_class=drainage,
                steward=steward,
            )
        )
    return plots


def _plantings_for_plot(ctx, rng, plot, varieties, realm):
    realm_methods = set(realm.get("signature_growing_methods") or ["open_field"])
    if plot["vertical_tier"] == "rooftop":
        realm_methods = {"rooftop_garden"}
    candidates = [
        v
        for v in varieties
        if plot["soil_class"] in v["preferred_soils"]
        and realm_methods & set(v["suited_methods"])
    ]
    if not candidates:
        return []
    plantings = []
    for _ in range(rng.randint(1, 2)):
        variety = rng.choice(candidates)
        method = rng.choice(sorted(realm_methods & set(variety["suited_methods"])))
        sown = dt.date(2026, rng.randint(1, 4), rng.randint(1, 28))
        plantings.append(
            ctx.add(
                "kelston.agriculture.planting",
                plot=plot["id"],
                variety=variety["id"],
                method=method,
                sown_on=sown.isoformat(),
                expected_first_harvest_on=(
                    sown + dt.timedelta(days=int(variety["typical_days_to_harvest"]))
                ).isoformat(),
            )
        )
    return plantings


def _harvests(ctx, rng, plot, planting, varieties):
    expected = dt.date.fromisoformat(planting["expected_first_harvest_on"])
    if expected > dt.date(2026, 6, 1):
        return []
    grades, weights = zip(*GRADE_WEIGHTS)
    harvests = []
    for round_number in range(rng.randint(1, 3)):
        harvested = expected + dt.timedelta(days=round_number * 14 + rng.randint(-3, 3))
        if harvested > dt.date(2026, 6, 10):
            break
        harvests.append(
            ctx.add(
                "kelston.agriculture.harvest_record",
                recorded_at=f"{harvested.isoformat()}T{rng.randint(5, 19):02d}:30:00",
                recorded_by=plot.get("steward"),
                planting=planting["id"],
                harvested_on=harvested.isoformat(),
                yield_mass=round(plot["area"] * rng.uniform(0.15, 1.8), 1),
                grade=rng.choices(grades, weights=weights)[0],
                harvested_by=plot.get("steward"),
            )
        )
    return harvests


def _food_products(ctx, rng):
    crafters = [
        o
        for o in ctx.all_of("kelston.core.organization")
        if o.get("industry") == "IND-agr-food-craft"
    ]
    product_names = {
        "fruit": ("orchard preserve", "pressed cordial"),
        "berry": ("cloudberry preserve", "berry shrub"),
        "grain": ("stoneground flour", "trail biscuit"),
        "legume": ("dry-stock beans", "pressed bean cake"),
        "nut": ("nut butter", "pressed nut oil"),
        "kelp": ("dried kelp sheet", "kelp broth base"),
        "root": ("cellar pickles", "root crisps"),
        "herb": ("tonic blend", "dried herb bundle"),
    }
    products = []
    for crafter in crafters:
        for _ in range(rng.randint(2, 4)):
            kind = rng.choice(sorted(product_names))
            name_options = product_names[kind]
            products.append(
                ctx.add(
                    "kelston.agriculture.food_product",
                    name=f"{crafter['name'].split(' ')[0]} {rng.choice(name_options)}",
                    made_by=crafter["id"],
                    main_crop_kind=kind,
                    shelf_life_duration=f"P{rng.choice([14, 30, 90, 180, 365])}D",
                    requires_cold_storage=rng.random() < 0.25,
                )
            )
    return products


def _market_lots(ctx, rng, harvests_by_farm, products, realms):
    varieties = {v["id"]: v for v in ctx.all_of("kelston.agriculture.crop_variety")}
    plantings = {p["id"]: p for p in ctx.all_of("kelston.agriculture.planting")}
    realm_ids = sorted(realms)
    lots = []
    for farm_id, harvests in sorted(harvests_by_farm.items()):
        farm = ctx.by_id[farm_id]
        for harvest in harvests:
            if rng.random() > 0.65:
                continue
            kind = varieties[plantings[harvest["planting"]]["variety"]]["crop_kind"]
            low, high = PRICE_BY_KIND[kind]
            offered = dt.date.fromisoformat(harvest["harvested_on"]) + dt.timedelta(days=1)
            lots.append(
                ctx.add(
                    "kelston.agriculture.market_lot",
                    seller=farm["id"],
                    harvest=harvest["id"],
                    lot_mass=round(harvest["yield_mass"] * rng.uniform(0.5, 0.95), 1),
                    unit_price=round(rng.uniform(low, high), 1),
                    offered_on=offered.isoformat(),
                    market_realm=farm["realm"] if rng.random() < 0.6 else realms[
                        rng.choice(realm_ids)
                    ]["id"],
                )
            )
    for product in products:
        maker = ctx.by_id[product["made_by"]]
        for _ in range(rng.randint(1, 3)):
            lots.append(
                ctx.add(
                    "kelston.agriculture.market_lot",
                    seller=maker["id"],
                    product=product["id"],
                    lot_mass=round(rng.uniform(5, 120), 1),
                    unit_price=round(rng.uniform(6, 22), 1),
                    offered_on=dt.date(2026, rng.randint(3, 6), rng.randint(1, 7)).isoformat(),
                    market_realm=maker["realm"],
                )
            )
    return lots


def _distribution_runs(ctx, rng, lots, realms):
    carriers = [
        o for o in ctx.all_of("kelston.core.organization") if o["sector"] == "mobility"
    ]
    if not carriers:
        return
    realm_ids = sorted(realms)
    for lot in lots:
        if rng.random() > 0.5:
            continue
        destination = rng.choice([r for r in realm_ids if r != lot["market_realm"]])
        delivered = dt.date.fromisoformat(lot["offered_on"]) + dt.timedelta(days=1)
        ctx.add(
            "kelston.agriculture.distribution_run",
            recorded_at=f"{delivered.isoformat()}T{rng.randint(5, 21):02d}:00:00",
            lot=lot["id"],
            carrier=rng.choice(carriers)["id"],
            destination_realm=destination,
            delivered_on=delivered.isoformat(),
            delivered_mass=round(lot["lot_mass"] * rng.uniform(0.9, 1.0), 1),
        )
