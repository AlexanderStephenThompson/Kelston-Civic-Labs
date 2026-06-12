"""Stage: citizens, households, and the dwellings that fit them.

This is the showcase of structural species traits: every home is generated
to honor the housing standard - clearance meets the largest resident,
semi-aquatic members get water access, ectotherms get basking provisions
(or the Drylands), and the validator later proves it independently.
"""

from __future__ import annotations

import datetime as dt

import yaml

from kelston import paths
from kelston.generate.context import GenContext

REALM_SHARES = {
    "commons": 0.26,
    "evergreen": 0.15,
    "canopy": 0.13,
    "frostlands": 0.09,
    "shorelines": 0.14,
    "highlands": 0.10,
    "drylands": 0.13,
}

HOUSEHOLD_SIZES = ([1] * 22 + [2] * 30 + [3] * 20 + [4] * 15 + [5] * 8 + [6] * 5)

# (max age, age of civic adulthood) per lifespan band - services are paced
# to each band, so a brief-band citizen is grown at three.
AGE_BANDS = {
    "brief": (15, 3),
    "standard": (40, 16),
    "long": (80, 18),
    "venerable": (110, 20),
}

PREFERENCE_BY_CYCLE = {
    "diurnal": ["day"],
    "nocturnal": ["night"],
    "crepuscular": ["dawn", "dusk"],
    "flexible": ["dawn", "day", "dusk", "night"],
}

DWELLING_KINDS_BY_REALM = {
    "commons": [("tower_flat", 45), ("courtyard_house", 30), ("burrow_home", 15), ("trunk_lodge", 10)],
    "evergreen": [("trunk_lodge", 40), ("burrow_home", 30), ("courtyard_house", 20), ("canopy_flat", 10)],
    "canopy": [("canopy_flat", 60), ("trunk_lodge", 25), ("courtyard_house", 15)],
    "frostlands": [("burrow_home", 40), ("courtyard_house", 35), ("tower_flat", 25)],
    "shorelines": [("shore_stilt", 50), ("courtyard_house", 25), ("tower_flat", 25)],
    "highlands": [("terrace_house", 60), ("tower_flat", 20), ("burrow_home", 20)],
    "drylands": [("courtyard_house", 45), ("terrace_house", 30), ("burrow_home", 25)],
}

TIER_BY_KIND = {"burrow_home": "burrow", "canopy_flat": "canopy"}

SIZE_ORDER = ["tiny", "small", "medium", "large", "grand"]


def run(ctx: GenContext) -> None:
    rng = ctx.rng("population")
    with open(paths.WORLD_DIR / "naming" / "names.yaml", encoding="utf-8") as handle:
        names = yaml.safe_load(handle)

    species_list = ctx.all_of("kelston.core.species_profile")
    realms = {r["realm_code"]: r for r in ctx.all_of("kelston.core.realm")}
    residential = {
        code: [
            p
            for p in ctx.all_of("kelston.core.parcel")
            if p["realm"] == realm["id"] and p["land_use"] in ("residential", "mixed")
        ]
        for code, realm in realms.items()
    }

    remaining = {
        code: round(share * ctx.population) for code, share in REALM_SHARES.items()
    }
    for realm_code, headcount in remaining.items():
        realm = realms[realm_code]
        weights = [
            4 if realm_code in (s.get("habitat_affinity") or []) else 1
            for s in species_list
        ]
        parcels = residential[realm_code]
        parcel_cursor = 0
        placed = 0
        while placed < headcount:
            size = min(rng.choice(HOUSEHOLD_SIZES), headcount - placed)
            members_species = _household_species(rng, species_list, weights, size)
            placed += size

            household_id = ctx.new_id("HSH")
            dwelling = _make_dwelling(
                ctx, rng, realm, parcels[parcel_cursor % len(parcels)], members_species
            )
            parcel_cursor += 1

            family_name = _family_name(rng, names, members_species[0])
            member_ids = []
            for index, species in enumerate(members_species):
                citizen = _make_citizen(
                    ctx, rng, names, species, realm, household_id, family_name, index
                )
                member_ids.append(citizen["id"])
            ctx.add(
                "kelston.core.household",
                instance_id=household_id,
                dwelling=dwelling["id"],
                household_name=f"the {family_name} household",
                members=member_ids,
            )


def _household_species(rng, species_list, weights, size) -> list[dict]:
    primary = rng.choices(species_list, weights=weights)[0]
    members = [primary]
    same_class = [s for s in species_list if s["animal_class"] == primary["animal_class"]]
    for _ in range(size - 1):
        roll = rng.random()
        if roll < 0.60:
            members.append(primary)
        elif roll < 0.85:
            members.append(rng.choice(same_class))
        else:
            members.append(rng.choices(species_list, weights=weights)[0])
    return members


def _family_name(rng, names, primary_species) -> str:
    pool_key = primary_species["animal_class"]
    if rng.random() < 0.4:
        return rng.choice(names["family_names"]["shared"])
    return rng.choice(names["family_names"][pool_key])


def _make_citizen(ctx, rng, names, species, realm, household_id, family_name, index):
    max_age, _adult = AGE_BANDS[species["lifespan_band"]]
    age = int(rng.triangular(0, max_age, max_age * 0.45))
    born_on = dt.date(2026 - age, rng.randint(1, 12), rng.randint(1, 28)).isoformat()

    bands = PREFERENCE_BY_CYCLE[species["activity_cycle"]]
    preference = rng.choice(bands)
    if rng.random() < 0.08:  # owls with day jobs exist
        preference = rng.choice(["dawn", "day", "dusk", "night"])

    # Children mostly share the family name; partners sometimes keep their own.
    own_name = family_name
    if index > 0 and rng.random() < 0.25:
        own_name = _family_name(rng, names, species)

    return ctx.add(
        "kelston.core.citizen",
        given_name=rng.choice(names["given_names"][species["animal_class"]]),
        family_name=own_name,
        species=species["id"],
        born_on=born_on,
        household=household_id,
        realm=realm["id"],
        active_hours_preference=preference,
    )


def _make_dwelling(ctx, rng, realm, parcel, members_species):
    realm_code = realm["realm_code"]
    kinds, weights = zip(*DWELLING_KINDS_BY_REALM[realm_code])
    kind = rng.choices(kinds, weights=weights)[0]

    largest = max(SIZE_ORDER.index(s["size_class"]) for s in members_species)
    clearance = SIZE_ORDER[min(largest + (1 if rng.random() < 0.2 else 0), 4)]

    any_semi_aquatic = any("semi_aquatic" in s["locomotion"] for s in members_species)
    any_flighted = any("flighted" in s["locomotion"] for s in members_species)
    any_fossorial = any("fossorial" in s["locomotion"] for s in members_species)
    any_ectotherm = any(s["thermoregulation"] == "ectotherm" for s in members_species)

    provision = "ambient"
    if any_ectotherm and realm_code != "drylands":
        provision = "heated_basking"
    elif realm_code == "drylands" and rng.random() < 0.2:
        provision = "cooled"
    elif realm_code == "frostlands" and rng.random() < 0.3:
        provision = "humidity_controlled"

    return ctx.add(
        "kelston.core.dwelling",
        realm=realm["id"],
        parcel=parcel["id"],
        vertical_tier=TIER_BY_KIND.get(kind, "ground"),
        dwelling_kind=kind,
        clearance_class=clearance,
        capacity=max(len(members_species), rng.randint(len(members_species), 8)),
        has_water_access=any_semi_aquatic or kind == "shore_stilt" or rng.random() < 0.05,
        has_flight_access=any_flighted or rng.random() < 0.10,
        has_burrow_level=any_fossorial or kind == "burrow_home" or rng.random() < 0.10,
        climate_provision=provision,
    )
