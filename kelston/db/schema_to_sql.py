"""Compile KSL schemas to SQLite tables and load the generated instances.

Scalars become typed columns, references become indexed TEXT columns
holding the target id, and lists/records are stored as JSON text. Every
row carries its conforms_to stamp.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from kelston.ksl.loader import Catalog

SQL_TYPES = {
    "id": "TEXT",
    "text": "TEXT",
    "integer": "INTEGER",
    "decimal": "REAL",
    "boolean": "INTEGER",
    "date": "TEXT",
    "time_of_day": "TEXT",
    "datetime": "TEXT",
    "duration": "TEXT",
    "quantity": "REAL",
    "vocab": "TEXT",
    "ref": "TEXT",
    "list": "TEXT",
    "record": "TEXT",
}


def table_name(schema_name: str) -> str:
    return schema_name.rsplit(".", 1)[-1]


def create_table_sql(schema_name: str, catalog: Catalog) -> list[str]:
    fields = catalog.resolved_fields(schema_name)
    columns = ["id TEXT PRIMARY KEY", "conforms_to TEXT NOT NULL"]
    indexes = []
    table = table_name(schema_name)
    for name, spec in fields.items():
        columns.append(f"{name} {SQL_TYPES[spec['type']]}")
        if spec["type"] == "ref":
            indexes.append(
                f"CREATE INDEX IF NOT EXISTS idx_{table}_{name} ON {table}({name})"
            )
    statements = [f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(columns)})"]
    statements.extend(indexes)
    return statements


def build_database(
    instances: dict[str, list[dict]], catalog: Catalog, db_path: Path
) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.unlink(missing_ok=True)
    connection = sqlite3.connect(db_path)
    try:
        for schema_name, rows in sorted(instances.items()):
            if not rows:
                continue
            for statement in create_table_sql(schema_name, catalog):
                connection.execute(statement)
            fields = catalog.resolved_fields(schema_name)
            column_names = ["id", "conforms_to", *fields]
            placeholders = ", ".join("?" for _ in column_names)
            insert = (
                f"INSERT INTO {table_name(schema_name)} "
                f"({', '.join(column_names)}) VALUES ({placeholders})"
            )
            for row in rows:
                values = []
                for column in column_names:
                    value = row.get(column)
                    if isinstance(value, (list, dict)):
                        value = json.dumps(value, sort_keys=True)
                    elif isinstance(value, bool):
                        value = int(value)
                    values.append(value)
                connection.execute(insert, values)
        connection.commit()
    finally:
        connection.close()
