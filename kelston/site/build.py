"""Assemble the Kelston civic portal: every page, from the town's own data."""

from __future__ import annotations

from pathlib import Path

from kelston import paths
from kelston.site import charts
from kelston.site.context import SiteData
from kelston.site.render import Page, copy_static, markdown_to_html, write_pages

SCHEMA_HREF = "standards/schemas/{}/index.html"
VOCAB_HREF = "standards/vocabularies/{}/index.html"


def build_site(output: Path | None = None) -> int:
    output = output or paths.SITE_DIR
    data = SiteData.load()
    shared = {
        "generation": data.generation,
        "totals": data.town_totals(),
        "breadcrumbs": [],
    }
    pages: list[Page] = []
    pages.append(_home(data))
    pages.extend(_realms(data))
    pages.extend(_standards(data))
    pages.append(_dashboards(data))
    count = write_pages(pages, output, shared)
    copy_static(output)
    return count


# ---- town & realms ---------------------------------------------------------


def _realm_populations(data: SiteData) -> dict[str, int]:
    by_name = dict(data.population_by_realm())
    return {r["realm_code"]: by_name[r["name"]] for r in data.realms}


def _home(data: SiteData) -> Page:
    return Page(
        rel_path="index.html",
        template="home.html",
        context={
            "realms": data.realms,
            "realm_populations": _realm_populations(data),
            "population_chart": charts.horizontal_bar(
                data.population_by_realm(), title="Population by realm"
            ),
        },
    )


def _realms(data: SiteData) -> list[Page]:
    populations = _realm_populations(data)
    pages = [
        Page(
            rel_path="realms/index.html",
            template="realms_index.html",
            context={
                "realms": data.realms,
                "realm_populations": populations,
                "breadcrumbs": [("Kelston", "index.html"), ("Realms", None)],
            },
        )
    ]
    for realm in data.realms:
        stats = data.realm_stats(realm)
        pages.append(
            Page(
                rel_path=f"realms/{realm['realm_code']}/index.html",
                template="realm.html",
                context={
                    "realm": realm,
                    "stats": stats,
                    "class_chart": charts.donut(
                        stats["class_mix"], title="Residents by citizen family"
                    ),
                    "species_chart": charts.horizontal_bar(
                        stats["top_species"], title="Most numerous species"
                    ),
                    "tier_chart": charts.horizontal_bar(
                        stats["tier_mix"], title="Homes by vertical tier"
                    ),
                    "climate_chart": charts.donut(
                        stats["climate_mix"], title="Climate provisions in homes"
                    ),
                    "shift_chart": charts.horizontal_bar(
                        stats["shift_mix"], title="Preferred active hours"
                    ),
                    "org_chart": charts.horizontal_bar(
                        stats["org_sectors"], title="Organizations by sector"
                    ),
                    "breadcrumbs": [
                        ("Kelston", "index.html"),
                        ("Realms", "realms/index.html"),
                        (realm["name"], None),
                    ],
                },
            )
        )
    return pages


# ---- standards registry ----------------------------------------------------


def _standards(data: SiteData) -> list[Page]:
    pages = [_standards_index(data), _changelog(data)]
    pages.append(_sector_page(data, None))
    for term in data.sectors:
        pages.append(_sector_page(data, term))
    for schema in data.catalog.schemas.values():
        pages.append(_schema_page(data, schema))
    for vocab in data.catalog.vocabularies.values():
        pages.append(_vocab_page(data, vocab))
    return pages


def _standards_index(data: SiteData) -> Page:
    schema_rows = []
    for name, schema in sorted(data.catalog.schemas.items()):
        schema_rows.append(
            {
                "name": name,
                "title": schema.title,
                "version": schema.version,
                "status": schema.status,
                "records": len(data.store.by_schema.get(name, [])),
                "search": f"{name} {schema.title}".lower(),
            }
        )
    vocab_rows = [
        {
            "name": name,
            "terms": len(vocab.terms),
            "version": vocab.version,
            "ordered": vocab.ordered,
            "search": f"{name} {' '.join(vocab.codes)}".lower(),
        }
        for name, vocab in sorted(data.catalog.vocabularies.items())
    ]
    sector_schema_counts = {
        term["code"]: len(data.schemas_of_sector(term["code"])) for term in data.sectors
    }
    return Page(
        rel_path="standards/index.html",
        template="standards_index.html",
        context={
            "sectors": data.sectors,
            "sector_schema_counts": sector_schema_counts,
            "core_count": len(data.schemas_of_sector("core")),
            "schema_rows": schema_rows,
            "vocab_rows": vocab_rows,
            "breadcrumbs": [("Kelston", "index.html"), ("Standards", None)],
        },
    )


def _sector_page(data: SiteData, term: dict | None) -> Page:
    if term is None:
        code, heading = "core", "Core standards"
        kicker = "The universal layer"
        description = (
            "The entities every sector shares: citizens, households, places, "
            "organizations, roles, and the civic record spine. A standard lives "
            "here only when two or more sectors must reference it by id."
        )
        stats = None
    else:
        code, heading = term["code"], term["label"]
        kicker = "Sector"
        description = term["description"]
        stats = data.sector_stats(code)
    return Page(
        rel_path=f"standards/{code}/index.html",
        template="sector.html",
        context={
            "kicker": kicker,
            "heading": heading,
            "description": description,
            "schemas": data.schemas_of_sector(code),
            "stats": stats,
            "breadcrumbs": [
                ("Kelston", "index.html"),
                ("Standards", "standards/index.html"),
                (heading, None),
            ],
        },
    )


def _schema_page(data: SiteData, schema) -> Page:
    group = schema.name.split(".")[1]
    if group == "core":
        kicker = "Core standard"
        group_href, group_label = "standards/core/index.html", "Core standards"
    else:
        kicker = data.vocab_label("kelston.vocab.sector", group)
        group_href, group_label = f"standards/{group}/index.html", kicker

    chain = [a for a in data.catalog.ancestors(schema.name) if a.name != schema.name]
    chain.reverse()  # nearest ancestor first

    constraints = [
        {
            "id": c["id"],
            "description": c.get("description", ""),
            "clause": _clause_text(c),
        }
        for c in data.catalog.resolved_constraints(schema.name)
    ]
    descendants = sorted(
        n for n in data.catalog.descendants(schema.name) if n != schema.name
    )
    entry = data.manifest["schemas"].get(schema.name)
    deps = [_dep(data, requirement) for requirement in (entry or {}).get("depends_on", [])]

    changelog_path = paths.CHANGELOG_DIR / f"{schema.name}.md"
    changelog_html = (
        markdown_to_html(changelog_path.read_text(encoding="utf-8"))
        if changelog_path.exists()
        else None
    )
    prefix = None
    for ancestor in reversed(data.catalog.ancestors(schema.name)):
        if ancestor.identity_prefix:
            prefix = ancestor.identity_prefix
            break
    return Page(
        rel_path=SCHEMA_HREF.format(schema.name),
        template="schema.html",
        context={
            "schema": schema,
            "kicker": kicker,
            "extends_chain": chain,
            "constraints": constraints,
            "descendants": descendants,
            "manifest_entry": entry,
            "deps": deps,
            "used_by": data.used_by.get(schema.name, []),
            "record_count": len(data.store.by_schema.get(schema.name, [])),
            "prefix": prefix,
            "changelog_html": changelog_html,
            "breadcrumbs": [
                ("Kelston", "index.html"),
                ("Standards", "standards/index.html"),
                (group_label, group_href),
                (schema.title, None),
            ],
        },
    )


def _vocab_page(data: SiteData, vocab) -> Page:
    return Page(
        rel_path=VOCAB_HREF.format(vocab.name),
        template="vocabulary.html",
        context={
            "vocab": vocab,
            "used_by": data.used_by.get(vocab.name, []),
            "manifest_entry": data.manifest["vocabularies"].get(vocab.name),
            "breadcrumbs": [
                ("Kelston", "index.html"),
                ("Standards", "standards/index.html"),
                (vocab.name.rsplit(".", 1)[-1], None),
            ],
        },
    )


def _changelog(data: SiteData) -> Page:
    history_rows = []
    for name, entry in sorted(
        data.manifest["schemas"].items(), key=lambda kv: -len(kv[1]["history"])
    ):
        history_rows.append(
            {
                "name": name,
                "href": SCHEMA_HREF.format(name),
                "current": entry["current"],
                "events": " ← ".join(
                    f"{e['version']} ({e['change']}, {e['date']})"
                    for e in reversed(entry["history"])
                ),
            }
        )
    legacy_files = sorted(paths.LEGACY_FIXTURES_DIR.glob("*.jsonl"))
    legacy_count = sum(
        sum(1 for line in f.read_text(encoding="utf-8").splitlines() if line.strip())
        for f in legacy_files
    )
    changelog_path = paths.CHANGELOG_DIR / "kelston.agriculture.growing_plot.md"
    return Page(
        rel_path="standards/changelog/index.html",
        template="changelog.html",
        context={
            "history_rows": history_rows,
            "legacy_count": legacy_count,
            "changelog_html": (
                markdown_to_html(changelog_path.read_text(encoding="utf-8"))
                if changelog_path.exists()
                else None
            ),
            "breadcrumbs": [
                ("Kelston", "index.html"),
                ("Standards", "standards/index.html"),
                ("Changelog", None),
            ],
        },
    )


# ---- dashboards --------------------------------------------------------------


def _dashboards(data: SiteData) -> Page:
    stats = data.dashboard_stats()
    rendered = {
        "population_by_realm": charts.horizontal_bar(
            stats["population_by_realm"], title="Population by realm"
        ),
        "class_by_realm": charts.stacked_bar(
            stats["class_by_realm"],
            stats["class_series"],
            title="Citizen families by realm",
        ),
        "size_mix": charts.horizontal_bar(
            stats["size_mix"], title="Citizens by size class"
        ),
        "residents_by_band": charts.horizontal_bar(
            stats["residents_by_band"], title="Preferred active hours"
        ),
        "worked_bands": charts.horizontal_bar(
            stats["worked_bands"], title="Appointments by shift band"
        ),
        "appointments_by_sector": charts.horizontal_bar(
            stats["appointments_by_sector"], title="Appointments by sector"
        ),
        "harvest_by_realm": charts.horizontal_bar(
            stats["harvest_by_realm"], title="Harvest by realm", unit="kg"
        ),
        "harvest_by_grade": charts.donut(
            stats["harvest_by_grade"], title="Harvest by produce grade"
        ),
        "lot_mass_by_realm": charts.horizontal_bar(
            stats["lot_mass_by_realm"], title="Market lot mass by realm", unit="kg"
        ),
        "climate_mix": charts.donut(
            stats["climate_mix"], title="Dwellings by climate provision"
        ),
    }
    return Page(
        rel_path="dashboards/index.html",
        template="dashboards.html",
        context={
            "charts": rendered,
            "breadcrumbs": [("Kelston", "index.html"), ("Dashboards", None)],
        },
    )


# ---- helpers -----------------------------------------------------------------


def _clause_text(constraint: dict) -> str:
    parts = []
    if "when" in constraint:
        parts.append(f"when {_clause(constraint['when'])}")
    if "check" in constraint:
        parts.append(f"check {_clause(constraint['check'])}")
    if constraint.get("rule"):
        parts.append(str(constraint["rule"]))
    return " · ".join(parts)


def _clause(clause: dict) -> str:
    target = clause.get("value", clause.get("other_field", ""))
    return f"{clause['field']} {clause['op']} {target}"


def _dep(data: SiteData, requirement: str) -> dict:
    name, _, pin = requirement.partition("@")
    href = (
        VOCAB_HREF.format(name)
        if name in data.catalog.vocabularies
        else SCHEMA_HREF.format(name)
    )
    return {"name": name, "pin": pin, "href": href}
