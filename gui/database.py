#!/usr/bin/env python3

import json

from rsqlite import transport


def execute_sql(query):
    response = transport.execute(query)

    if isinstance(response, str):
        return json.loads(response)

    return response


def get_tables():
    response = execute_sql(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """
    )

    if not response.get("ok"):
        raise RuntimeError(
            response.get("error", "Unable to retrieve tables")
        )

    return [row[0] for row in response.get("rows", [])]


def browse_table(table_name):
    response = execute_sql(
        f"SELECT * FROM {table_name}"
    )

    if not response.get("ok"):
        raise RuntimeError(
            response.get("error", "Unable to browse table")
        )

    return {
        "columns": response.get("columns", []),
        "rows": response.get("rows", []),
    }


def get_schema(table_name):
    response = execute_sql(
        f"PRAGMA table_info({table_name})"
    )

    if not response.get("ok"):
        raise RuntimeError(
            response.get("error", "Unable to retrieve table schema")
        )

    return {
        "columns": response.get("columns", []),
        "rows": response.get("rows", []),
    }
