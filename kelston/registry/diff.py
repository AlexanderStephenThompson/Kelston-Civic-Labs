"""Diff two versions of a standard and classify the change.

The classifier is what makes versioning honest: PATCH/MINOR/MAJOR is
computed from what actually changed, not from what the editor hoped.
"""

from __future__ import annotations

LEVELS = ["patch", "minor", "major"]


def _worst(current: str, candidate: str) -> str:
    return candidate if LEVELS.index(candidate) > LEVELS.index(current) else current


def diff_schema(old: dict, new: dict) -> tuple[str, list[str]]:
    """Compare two schema documents; return (level, human changelog lines)."""
    level = "patch"
    changes: list[str] = []
    old_fields = old.get("fields") or {}
    new_fields = new.get("fields") or {}

    for name in sorted(set(old_fields) - set(new_fields)):
        changes.append(f"removed field `{name}`")
        level = _worst(level, "major")
    for name in sorted(set(new_fields) - set(old_fields)):
        if new_fields[name].get("required"):
            changes.append(f"added required field `{name}`")
            level = _worst(level, "major")
        else:
            changes.append(f"added optional field `{name}`")
            level = _worst(level, "minor")
    for name in sorted(set(old_fields) & set(new_fields)):
        before, after = old_fields[name], new_fields[name]
        for key in ("type", "vocabulary", "entity", "unit"):
            if before.get(key) != after.get(key):
                changes.append(
                    f"changed `{name}.{key}`: {before.get(key)!r} -> {after.get(key)!r}"
                )
                level = _worst(level, "major")
        if bool(before.get("required")) != bool(after.get("required")):
            if after.get("required"):
                changes.append(f"made `{name}` required")
                level = _worst(level, "major")
            else:
                changes.append(f"made `{name}` optional")
                level = _worst(level, "minor")
        if before.get("default") != after.get("default"):
            changes.append(f"changed `{name}` default to {after.get('default')!r}")
            level = _worst(level, "minor")
        if before.get("description") != after.get("description"):
            changes.append(f"reworded `{name}` description")

    old_rules = {c.get("id"): c for c in old.get("constraints") or []}
    new_rules = {c.get("id"): c for c in new.get("constraints") or []}
    for rule_id in sorted(set(new_rules) - set(old_rules)):
        changes.append(f"added constraint `{rule_id}`")
        level = _worst(level, "major")
    for rule_id in sorted(set(old_rules) - set(new_rules)):
        changes.append(f"removed constraint `{rule_id}`")
        level = _worst(level, "minor")
    for rule_id in sorted(set(old_rules) & set(new_rules)):
        if old_rules[rule_id] != new_rules[rule_id]:
            changes.append(f"changed constraint `{rule_id}`")
            level = _worst(level, "major")

    for key in ("title", "description", "status"):
        if old.get(key) != new.get(key):
            changes.append(f"updated `{key}`")
    if old.get("extends") != new.get("extends"):
        changes.append(f"changed parent: {old.get('extends')!r} -> {new.get('extends')!r}")
        level = _worst(level, "major")
    return level, changes


def diff_vocabulary(old: dict, new: dict) -> tuple[str, list[str]]:
    level = "patch"
    changes: list[str] = []
    old_terms = {t["code"]: t for t in old.get("terms") or []}
    new_terms = {t["code"]: t for t in new.get("terms") or []}
    for code in sorted(set(old_terms) - set(new_terms)):
        changes.append(f"removed term `{code}`")
        level = _worst(level, "major")
    for code in sorted(set(new_terms) - set(old_terms)):
        changes.append(f"added term `{code}`")
        level = _worst(level, "minor")
    for code in sorted(set(old_terms) & set(new_terms)):
        if old_terms[code] != new_terms[code]:
            changes.append(f"reworded term `{code}`")
    if bool(old.get("ordered")) != bool(new.get("ordered")):
        changes.append("changed `ordered`")
        level = _worst(level, "major")
    if list(old_terms) != list(new_terms) and old.get("ordered"):
        changes.append("reordered terms of an ordered vocabulary")
        level = _worst(level, "major")
    if old.get("description") != new.get("description"):
        changes.append("updated vocabulary description")
    return level, changes
