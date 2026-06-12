"""The closed KSL type system.

Every field in every Kelston schema uses one of these types. Scalar checks
live here; vocabulary, reference, and constraint checks need the catalog and
live in the validator.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

SCALAR_TYPES = {
    "id",
    "text",
    "integer",
    "decimal",
    "boolean",
    "date",
    "time_of_day",
    "datetime",
    "duration",
    "quantity",
}
COMPOSITE_TYPES = {"vocab", "ref", "list", "record"}
ALL_TYPES = SCALAR_TYPES | COMPOSITE_TYPES

# Which extra keys each type requires on its field definition.
REQUIRED_TYPE_KEYS = {
    "quantity": ["unit"],
    "vocab": ["vocabulary"],
    "ref": ["entity"],
    "list": ["items"],
    "record": ["fields"],
}

_TIME_OF_DAY_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
# ISO-8601-ish durations kept deliberately simple: P3D, PT2H, P1DT4H30M
_DURATION_RE = re.compile(r"^P(?=.)(\d+D)?(T(?=.)(\d+H)?(\d+M)?)?$")
_ID_RE = re.compile(r"^[A-Z][A-Z0-9]{1,7}-[A-Za-z0-9-]+$")


def check_scalar(type_name: str, value: Any) -> str | None:
    """Return an error message if value does not conform to the scalar type."""
    if type_name == "id":
        if not isinstance(value, str) or not _ID_RE.match(value):
            return f"expected an id like 'PLOT-000482', got {value!r}"
    elif type_name == "text":
        if not isinstance(value, str):
            return f"expected text, got {type(value).__name__}"
    elif type_name == "integer":
        if not isinstance(value, int) or isinstance(value, bool):
            return f"expected an integer, got {value!r}"
    elif type_name == "decimal":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return f"expected a number, got {value!r}"
    elif type_name == "boolean":
        if not isinstance(value, bool):
            return f"expected true/false, got {value!r}"
    elif type_name == "date":
        if not _is_iso_date(value):
            return f"expected an ISO date (YYYY-MM-DD), got {value!r}"
    elif type_name == "time_of_day":
        if not isinstance(value, str) or not _TIME_OF_DAY_RE.match(value):
            return f"expected a time of day (HH:MM), got {value!r}"
    elif type_name == "datetime":
        if not _is_iso_datetime(value):
            return f"expected an ISO datetime, got {value!r}"
    elif type_name == "duration":
        if not isinstance(value, str) or not _DURATION_RE.match(value):
            return f"expected an ISO duration (e.g. P3D, PT2H), got {value!r}"
    elif type_name == "quantity":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return f"expected a bare number (unit lives in the schema), got {value!r}"
    else:
        return f"unknown scalar type {type_name!r}"
    return None


def _is_iso_date(value: Any) -> bool:
    if isinstance(value, date) and not isinstance(value, datetime):
        return True
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def _is_iso_datetime(value: Any) -> bool:
    if isinstance(value, datetime):
        return True
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value)
        return True
    except ValueError:
        return False
