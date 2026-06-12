from kelston.ksl.constraints import check_constraint, evaluate_clause
from kelston.ksl.loader import load_catalog
from kelston.ksl.validator import Store

CATALOG = load_catalog()


def make_store(*instances):
    store = Store()
    for instance in instances:
        store.add(instance)
    return store


SPECIES = {
    "id": "SPC-test-croc",
    "conforms_to": "kelston.core.species_profile@1.0.0",
    "size_class": "large",
    "locomotion": ["semi_aquatic", "terrestrial"],
    "thermoregulation": "ectotherm",
}
CITIZEN = {
    "id": "CTZ-000001",
    "conforms_to": "kelston.core.citizen@1.0.0",
    "species": "SPC-test-croc",
}


def test_dotted_paths_traverse_references():
    store = make_store(SPECIES, CITIZEN)
    clause = {"field": "species.size_class", "op": "eq", "value": "large"}
    assert evaluate_clause(clause, CITIZEN, store, CATALOG)


def test_ordered_vocab_comparison():
    store = make_store(SPECIES, CITIZEN)
    clause = {
        "field": "species.size_class",
        "op": "gte",
        "value": "medium",
        "vocabulary": "kelston.vocab.size_class",
    }
    assert evaluate_clause(clause, CITIZEN, store, CATALOG)
    clause["value"] = "grand"
    assert not evaluate_clause(clause, CITIZEN, store, CATALOG)


def test_contains_on_list_traits():
    store = make_store(SPECIES, CITIZEN)
    clause = {"field": "species.locomotion", "op": "contains", "value": "semi_aquatic"}
    assert evaluate_clause(clause, CITIZEN, store, CATALOG)
    clause["value"] = "flighted"
    assert not evaluate_clause(clause, CITIZEN, store, CATALOG)


def test_when_guard_skips_check():
    store = make_store(SPECIES, CITIZEN)
    constraint = {
        "id": "only_for_flighted",
        "when": {"field": "species.locomotion", "op": "contains", "value": "flighted"},
        "check": {"field": "species.size_class", "op": "eq", "value": "tiny"},
    }
    assert check_constraint(constraint, CITIZEN, store, CATALOG) is None


def test_violation_reports_constraint_id():
    store = make_store(SPECIES, CITIZEN)
    constraint = {
        "id": "crocs_must_be_tiny",
        "check": {"field": "species.size_class", "op": "eq", "value": "tiny"},
    }
    message = check_constraint(constraint, CITIZEN, store, CATALOG)
    assert message is not None and "crocs_must_be_tiny" in message
