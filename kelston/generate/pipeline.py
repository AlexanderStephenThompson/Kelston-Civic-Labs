"""The generation pipeline: ordered stages, one shared context."""

from __future__ import annotations

from kelston.generate import emit
from kelston.generate.context import GenContext
from kelston.generate.stages import agriculture, economy, population, world
from kelston.ksl.loader import Catalog, load_catalog

STAGES = [
    ("world", world.run),
    ("population", population.run),
    ("economy", economy.run),
    ("agriculture", agriculture.run),
]


def generate(seed: int = 42, population_size: int = 5000, catalog: Catalog | None = None) -> GenContext:
    ctx = GenContext(
        seed=seed, catalog=catalog or load_catalog(), population=population_size
    )
    for _name, stage in STAGES:
        stage(ctx)
    return ctx


def generate_and_emit(seed: int = 42, population_size: int = 5000) -> GenContext:
    ctx = generate(seed=seed, population_size=population_size)
    emit.emit_fixtures(ctx)
    emit.emit_database(ctx)
    return ctx
