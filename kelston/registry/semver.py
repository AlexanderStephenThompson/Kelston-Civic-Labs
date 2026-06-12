"""Just enough semantic-version handling for the registry."""

from __future__ import annotations


def parse(version: str) -> tuple[int, int, int]:
    major, minor, patch = (int(part) for part in version.split("."))
    return major, minor, patch


def bump(version: str, level: str) -> str:
    major, minor, patch = parse(version)
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    if level == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"unknown bump level {level!r}")


def compatible(version: str, requirement: str) -> bool:
    """Caret ranges only: 'name@^2' style requirements pin the major."""
    if requirement.startswith("^"):
        return parse(version)[0] == int(requirement[1:].split(".")[0])
    return version == requirement


def matches_range(version: str, expression: str) -> bool:
    """Match a version against a migration's `from` expression.

    Supported forms: exact '1.2.0', wildcard '1.x',
    and space-separated comparators '>=1.0.0 <2.0.0'.
    """
    expression = expression.strip()
    if expression.endswith(".x"):
        return parse(version)[0] == int(expression[:-2])
    if any(expression.startswith(op) for op in (">=", "<", ">", "<=")):
        value = parse(version)
        for clause in expression.split():
            for op in (">=", "<=", ">", "<"):
                if clause.startswith(op):
                    bound = parse(clause[len(op):])
                    ok = {
                        ">=": value >= bound,
                        "<=": value <= bound,
                        ">": value > bound,
                        "<": value < bound,
                    }[op]
                    if not ok:
                        return False
                    break
            else:
                raise ValueError(f"bad range clause {clause!r}")
        return True
    return version == expression
