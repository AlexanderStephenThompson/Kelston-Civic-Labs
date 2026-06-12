"""Python rules for the core layer."""

from __future__ import annotations

from kelston.ksl.constraints import MISSING, RuleContext

# Which species traits satisfy each capability a role can require.
CAPABILITY_TRAITS = {
    "flight": ("locomotion", {"flighted"}),
    "climbing": ("locomotion", {"arboreal", "flighted"}),
    "swimming": ("locomotion", {"semi_aquatic"}),
    "burrowing": ("locomotion", {"fossorial"}),
    "night_work": ("activity_cycle", {"nocturnal", "crepuscular", "flexible"}),
    "heavy_handling": ("size_class", {"large", "grand"}),
    "fine_handling": ("size_class", {"tiny", "small"}),
}


def ectotherm_home_is_warm_enough(instance: dict, ctx: RuleContext) -> str | None:
    """An ectotherm's home provides basking heat, unless the home stands in
    the Drylands where the realm itself is the basking ground."""
    provision = ctx.resolve(instance, "household.dwelling.climate_provision")
    realm_code = ctx.resolve(instance, "household.dwelling.realm.realm_code")
    if provision == "heated_basking" or realm_code == "drylands":
        return None
    return f"climate_provision is {provision!r} in realm {realm_code!r}"


def household_within_capacity(instance: dict, ctx: RuleContext) -> str | None:
    members = instance.get("members") or []
    capacity = ctx.resolve(instance, "dwelling.capacity")
    if capacity is MISSING or len(members) <= capacity:
        return None
    return f"{len(members)} members in a home built for {capacity}"


def citizen_meets_role_capabilities(instance: dict, ctx: RuleContext) -> str | None:
    required = ctx.resolve(instance, "role.required_capabilities")
    if required is MISSING or not required:
        return None
    for capability in required:
        trait_field, satisfying = CAPABILITY_TRAITS[capability]
        trait = ctx.resolve(instance, f"citizen.species.{trait_field}")
        values = set(trait) if isinstance(trait, list) else {trait}
        if not values & satisfying:
            return f"requires {capability}, but species {trait_field} is {sorted(values)}"
    return None
