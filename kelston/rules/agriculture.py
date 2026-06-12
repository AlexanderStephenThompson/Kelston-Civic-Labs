"""Python rules and migration derivers for the agriculture sector."""

from __future__ import annotations

from kelston.ksl.constraints import MISSING, RuleContext


def semi_aquatic_steward_check(instance: dict, ctx: RuleContext) -> str | None:
    """A submerged plot's steward, if it has one, must be fully at home in
    the water."""
    steward = instance.get("steward")
    if not steward:
        return None
    locomotion = ctx.resolve(instance, "steward.species.locomotion")
    if locomotion is MISSING or "semi_aquatic" in locomotion:
        return None
    return f"steward's species locomotion is {locomotion}"


def lot_has_one_source(instance: dict, ctx: RuleContext) -> str | None:
    has_harvest = bool(instance.get("harvest"))
    has_product = bool(instance.get("product"))
    if has_harvest == has_product:
        return "needs exactly one of harvest or product"
    return None


# --- migration derivers ----------------------------------------------------

# Legacy 1.x soil codes that folded texture and drainage together.
LEGACY_DRAINAGE = {
    "loam_wet": "water_holding",
    "loam_dry": "free_draining",
    "clay_heavy": "water_holding",
}


def derive_drainage_from_legacy_soil(instance: dict) -> str:
    """growing_plot 2.0.0: drainage_class from the legacy combined soil code,
    falling back to what the kept soil class implies."""
    legacy = instance.get("soil_class")
    if legacy in LEGACY_DRAINAGE:
        return LEGACY_DRAINAGE[legacy]
    return {
        "sand": "free_draining",
        "volcanic": "free_draining",
        "clay": "water_holding",
        "peat": "water_holding",
        "substrate_water": "water_holding",
    }.get(legacy, "moderate")
