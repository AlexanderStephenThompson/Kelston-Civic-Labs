from kelston.generate.pipeline import generate
from kelston.ksl.loader import load_catalog
from kelston.ksl.validator import Store, validate_store

CATALOG = load_catalog()


def build_store(ctx) -> Store:
    store = Store()
    for rows in ctx.instances.values():
        for row in rows:
            store.add(row)
    return store


def test_generated_town_is_valid():
    ctx = generate(seed=7, population_size=600, catalog=CATALOG)
    errors = validate_store(build_store(ctx), CATALOG)
    assert errors == []


def test_same_seed_same_town():
    first = generate(seed=11, population_size=300, catalog=CATALOG)
    second = generate(seed=11, population_size=300, catalog=CATALOG)
    assert first.instances == second.instances


def test_different_seed_different_town():
    first = generate(seed=11, population_size=300, catalog=CATALOG)
    second = generate(seed=12, population_size=300, catalog=CATALOG)
    assert first.instances != second.instances


def test_housing_guarantees_hold_by_construction():
    """The dwelling solver honors the standard before the validator checks it."""
    ctx = generate(seed=5, population_size=400, catalog=CATALOG)
    species = {s["id"]: s for s in ctx.all_of("kelston.core.species_profile")}
    order = ["tiny", "small", "medium", "large", "grand"]
    for household in ctx.all_of("kelston.core.household"):
        dwelling = ctx.by_id[household["dwelling"]]
        for member_id in household["members"]:
            member_species = species[ctx.by_id[member_id]["species"]]
            assert order.index(dwelling["clearance_class"]) >= order.index(
                member_species["size_class"]
            )
            if "semi_aquatic" in member_species["locomotion"]:
                assert dwelling["has_water_access"]
