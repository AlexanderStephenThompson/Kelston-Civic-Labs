"""Stage: organizations across all seventeen sectors, then employment -
appointments that respect role capability requirements and pair shift
bands with citizens' own active hours."""

from __future__ import annotations

import datetime as dt
from collections import defaultdict

from kelston.generate.context import GenContext
from kelston.generate.stages.population import AGE_BANDS
from kelston.rules.core import CAPABILITY_TRAITS

ORG_COUNTS = {
    "agriculture": 58,
    "commerce": 40,
    "making": 28,
    "housing": 24,
    "education": 20,
    "health": 18,
    "care": 18,
    "arts": 16,
    "mobility": 16,
    "utilities": 14,
    "recreation": 14,
    "governance": 12,
    "safety": 12,
    "environment": 10,
    "science": 8,
    "finance": 8,
    "media": 8,
}

ORG_SUFFIXES = ["Cooperative", "Works", "Guild", "Hall", "Collective", "Circle", "Office"]

CYCLE_WEIGHTS_BY_SECTOR = {
    "health": [("daytime", 5), ("evening", 1), ("continuous", 4)],
    "safety": [("daytime", 2), ("evening", 2), ("continuous", 6)],
    "mobility": [("daytime", 4), ("evening", 2), ("continuous", 4)],
    "utilities": [("daytime", 5), ("evening", 1), ("continuous", 4)],
    "commerce": [("daytime", 6), ("evening", 3), ("continuous", 1)],
    "arts": [("daytime", 4), ("evening", 6)],
}
DEFAULT_CYCLE_WEIGHTS = [("daytime", 8), ("evening", 1), ("continuous", 1)]

BANDS_BY_CYCLE = {
    "daytime": ["dawn", "day"],
    "evening": ["dusk", "night"],
    "continuous": ["dawn", "day", "dusk", "night"],
}

# Industries whose agriculture organizations are full farm records.
FARM_INDUSTRIES = {"IND-agr-growing", "IND-agr-orcharding", "IND-agr-aquaponics"}

EMPLOYMENT_RATE = 0.62
REFERENCE_DATE = dt.date(2026, 6, 1)


def run(ctx: GenContext) -> None:
    _organizations(ctx)
    _employment(ctx)


def _organizations(ctx: GenContext) -> None:
    rng = ctx.rng("organizations")
    realms = ctx.all_of("kelston.core.realm")
    industries_by_sector: dict[str, list[dict]] = defaultdict(list)
    for industry in ctx.all_of("kelston.core.industry"):
        industries_by_sector[industry["sector"]].append(industry)

    farm_parcels = {
        realm["id"]: [
            p
            for p in ctx.all_of("kelston.core.parcel")
            if p["realm"] == realm["id"] and p["land_use"] == "agricultural"
        ]
        for realm in realms
    }

    for sector, count in ORG_COUNTS.items():
        industries = industries_by_sector.get(sector)
        if not industries:
            continue  # sector taxonomy not authored yet
        for _ in range(count):
            industry = rng.choice(industries)
            realm = rng.choice(realms)
            # The Drylands runs on the evening; nudge its workplaces there.
            cycle_weights = CYCLE_WEIGHTS_BY_SECTOR.get(sector, DEFAULT_CYCLE_WEIGHTS)
            if realm["realm_code"] == "drylands":
                cycle_weights = [("evening", 5), ("continuous", 2), ("daytime", 3)]
            cycles, weights = zip(*cycle_weights)
            common = dict(
                name=_org_name(rng, realm, industry),
                sector=sector,
                industry=industry["id"],
                realm=realm["id"],
                operating_cycle=rng.choices(cycles, weights=weights)[0],
                founded_on=dt.date(
                    rng.randint(1968, 2024), rng.randint(1, 12), rng.randint(1, 28)
                ).isoformat(),
            )
            if sector == "agriculture" and industry["id"] in FARM_INDUSTRIES:
                parcels = farm_parcels[realm["id"]] or ctx.all_of("kelston.core.parcel")
                methods = realm.get("signature_growing_methods") or ["open_field"]
                ctx.add(
                    "kelston.agriculture.farm",
                    home_parcel=rng.choice(parcels)["id"],
                    total_growing_area=round(rng.uniform(2000, 30000)),
                    primary_methods=methods,
                    is_commons=rng.random() < 0.15,
                    **common,
                )
            else:
                ctx.add("kelston.core.organization", **common)


def _org_name(rng, realm, industry) -> str:
    return f"{realm['name'].removeprefix('The ')} {industry['name']} {rng.choice(ORG_SUFFIXES)}"


def _employment(ctx: GenContext) -> None:
    rng = ctx.rng("employment")
    species_by_id = {s["id"]: s for s in ctx.all_of("kelston.core.species_profile")}
    roles_by_industry: dict[str, list[dict]] = defaultdict(list)
    for role in ctx.all_of("kelston.core.role"):
        roles_by_industry[role["industry"]].append(role)

    adults = [
        c
        for c in ctx.all_of("kelston.core.citizen")
        if _age(c) >= AGE_BANDS[species_by_id[c["species"]]["lifespan_band"]][1]
    ]
    rng.shuffle(adults)
    available: dict[str, list[dict]] = defaultdict(list)  # realm id -> citizens
    for citizen in adults:
        available[citizen["realm"]].append(citizen)
    target_jobs = int(len(adults) * EMPLOYMENT_RATE)
    placed = 0

    organizations = list(ctx.all_of("kelston.core.organization")) + list(
        ctx.all_of("kelston.agriculture.farm")
    )
    # Hire in shuffled order so late-listed employers (the farms) are not
    # starved when the town reaches full employment first.
    rng.shuffle(organizations)
    for org in organizations:
        if placed >= target_jobs:
            break
        roles = roles_by_industry.get(org["industry"])
        if not roles:
            continue
        headcount = rng.randint(3, 10) if "farm" in org["conforms_to"] else rng.randint(2, 16)
        allowed_bands = BANDS_BY_CYCLE[org["operating_cycle"]]
        for _ in range(headcount):
            if placed >= target_jobs:
                break
            role = rng.choice(roles)
            citizen = _find_worker(rng, available, org, role, species_by_id, allowed_bands)
            if citizen is None:
                continue
            band = (
                citizen["active_hours_preference"]
                if citizen["active_hours_preference"] in allowed_bands
                else rng.choice(allowed_bands)
            )
            adulthood = AGE_BANDS[species_by_id[citizen["species"]]["lifespan_band"]][1]
            earliest = max(2010, 2026 - (_age(citizen) - adulthood))
            ctx.add(
                "kelston.core.appointment",
                citizen=citizen["id"],
                role=role["id"],
                organization=org["id"],
                began_on=dt.date(
                    rng.randint(earliest, 2026), rng.randint(1, 5), rng.randint(1, 28)
                ).isoformat(),
                shift_band=band,
            )
            placed += 1


def _find_worker(rng, available, org, role, species_by_id, allowed_bands):
    """Prefer workers from the organization's own realm whose traits satisfy
    the role and whose preferred hours fit the operating cycle."""
    pools = [available[org["realm"]]]
    pools.append([c for realm_pool in available.values() for c in realm_pool])
    for strict_band in (True, False):
        for pool in pools:
            for citizen in pool:
                species = species_by_id[citizen["species"]]
                if not _meets(role, species):
                    continue
                if strict_band and citizen["active_hours_preference"] not in allowed_bands:
                    continue
                for realm_pool in available.values():
                    if citizen in realm_pool:
                        realm_pool.remove(citizen)
                return citizen
    return None


def _meets(role, species) -> bool:
    for capability in role.get("required_capabilities") or []:
        trait_field, satisfying = CAPABILITY_TRAITS[capability]
        trait = species[trait_field]
        values = set(trait) if isinstance(trait, list) else {trait}
        if not values & satisfying:
            return False
    return True


def _age(citizen) -> int:
    born = dt.date.fromisoformat(citizen["born_on"])
    return (REFERENCE_DATE - born).days // 365
