"""The portal builds completely, covers the whole catalog, and contains
no broken internal links."""

import re
from collections import Counter
from pathlib import Path

import pytest

from kelston.ksl.loader import load_catalog
from kelston.ksl.validator import Store
from kelston import paths
from kelston.site import charts
from kelston.site.build import build_site

CATALOG = load_catalog()


@pytest.fixture(scope="module")
def site(tmp_path_factory) -> Path:
    output = tmp_path_factory.mktemp("site")
    build_site(output)
    return output


def test_keystone_pages_exist(site):
    for rel in [
        "index.html",
        "realms/index.html",
        "standards/index.html",
        "standards/core/index.html",
        "standards/changelog/index.html",
        "dashboards/index.html",
        "static/style.css",
        "static/filter.js",
    ]:
        assert (site / rel).exists(), rel


def test_every_standard_has_a_page(site):
    for name in CATALOG.schemas:
        assert (site / "standards" / "schemas" / name / "index.html").exists(), name
    for name in CATALOG.vocabularies:
        assert (site / "standards" / "vocabularies" / name / "index.html").exists(), name
    for term in CATALOG.vocabularies["kelston.vocab.sector"].terms:
        assert (site / "standards" / term["code"] / "index.html").exists(), term["code"]


def test_every_realm_has_a_page(site):
    store = Store.from_fixture_dir(paths.FIXTURES_DIR)
    for realm in store.by_schema["kelston.core.realm"]:
        assert (site / "realms" / realm["realm_code"] / "index.html").exists()


HREF_RE = re.compile(r'(?:href|src)="([^"]+)"')


def test_no_broken_internal_links(site):
    broken = []
    for page in site.rglob("*.html"):
        for target in HREF_RE.findall(page.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target_path = (page.parent / target.split("#")[0]).resolve()
            if target_path.is_dir():
                target_path = target_path / "index.html"
            if not target_path.exists():
                broken.append(f"{page.relative_to(site)} -> {target}")
    assert broken == []


def test_growing_plot_page_shows_the_version_story(site):
    page = (
        site / "standards" / "schemas" / "kelston.agriculture.growing_plot" / "index.html"
    ).read_text(encoding="utf-8")
    assert "2.0.0" in page
    assert "drainage_class" in page
    assert "1.2.0" in page  # history table
    assert "migration" in page.lower()


def test_realm_page_shows_real_population(site):
    store = Store.from_fixture_dir(paths.FIXTURES_DIR)
    commons = next(
        r for r in store.by_schema["kelston.core.realm"] if r["realm_code"] == "commons"
    )
    population = Counter(
        c["realm"] for c in store.by_schema["kelston.core.citizen"]
    )[commons["id"]]
    page = (site / "realms" / "commons" / "index.html").read_text(encoding="utf-8")
    assert f"{population:,}" in page


# ---- chart unit tests -------------------------------------------------------


def test_horizontal_bar_structure_and_escaping():
    svg = charts.horizontal_bar([("a<b", 3), ("plain", 1)], title="Test & chart")
    assert svg.startswith("<svg")
    assert "<title" in svg
    assert "a&lt;b" in svg
    assert "Test &amp; chart" in svg


def test_donut_handles_zero_and_empty():
    assert "<svg" in charts.donut([("x", 0), ("y", 5)], title="t")
    assert "<svg" in charts.donut([], title="empty")


def test_stacked_bar_totals():
    svg = charts.stacked_bar(
        [("row", {"a": 2, "b": 3})], ["a", "b"], title="stack"
    )
    assert ">5<" in svg  # total label rendered
