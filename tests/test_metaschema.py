from kelston.ksl.loader import load_catalog
from kelston.ksl.metaschema import check_catalog


def test_every_standard_conforms_to_ksl():
    errors = check_catalog(load_catalog())
    assert errors == []
