"""
Provide database access functions for the rSQLite NomadNet GUI.

Responsibilities:
    - Execute SQL queries through the rSQLite transport layer and normalize
      JSON responses into Python objects.
    - Retrieve database table names, count records and browse table contents.
    - Retrieve table schemas, including column definitions and primary keys.
    - Insert new records and retrieve individual records by primary key.
    - Update existing records and delete records using their primary keys.
    - Check query results and raise exceptions when database operations fail.
"""

import json

from rsqlite import transport

def execute_sql(query):
    """Execute a SQL query through the transport layer 
    and parse its response."""
    response = transport.execute(query)

    if isinstance(response, str):
        return json.loads(response)

    return response


def get_tables():
    """Return the names of the tables in the remote database."""
    response = execute_sql("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """)

    if not response.get("ok"):
        raise RuntimeError(response.get("error", "Database error"))
    
    return [row[0] for row in response.get("rows", [])]


def count_records(table_name):
    """Return the column names and record count for a table."""
    response = execute_sql(f"""
        SELECT COUNT(*)
        FROM "{table_name}"
    """)

    if not response.get("ok"):
        raise RuntimeError(
            response.get("error", "Database error")
        )

    return {
        "columns": response.get("columns", []),
        "rows": response.get("rows", []),
    }


def browse_table(table_name, limit=20, offset=0):
    """Retrieve a range of records from a table using pagination."""
    response = execute_sql(f"""
        SELECT *
        FROM "{table_name}"
        LIMIT {limit}
        OFFSET {offset}
    """)

    if not response.get("ok"):
        raise RuntimeError(
            response.get("error", "Database error")
        )

    return {
        "columns": response.get("columns", []),
        "rows": response.get("rows", []),
    }


def get_schema(table_name):
    """Retrieve a table's schema, returning its columns and rows."""
    response = execute_sql(
        f'PRAGMA table_info("{table_name}")'
    )

    if not response.get("ok"):
        raise RuntimeError(
            response.get("error", "Database error")
        )

    return {
        "columns": response.get("columns", []),
        "rows": response.get("rows", []),
    }


def insert_record(table_name, values):
    """Insert a new record into a table using the supplied column values."""
    columns = []
    sql_values = []

    for column_name, value in values.items():

        columns.append(
            f'"{column_name}"'
        )

        if value is None:
            sql_values.append("NULL")
        else:
            escaped = str(value).replace("'", "''")
            sql_values.append(
                f"'{escaped}'"
            )

    if not columns:
        raise RuntimeError(
            "No values to insert"
        )

    query = f'''
        INSERT INTO "{table_name}"
        ({", ".join(columns)})
        VALUES
        ({", ".join(sql_values)})
    '''

    response = execute_sql(query)

    if not response.get("ok"):
        raise RuntimeError(
            response.get("error", "Insert failed")
        )

    return response


def get_record(table_name, primary_key, primary_key_value):
    """Retrieve a single record by its primary key."""
    escaped_value = str(
        primary_key_value
    ).replace("'", "''")

    query = f'''
        SELECT *
        FROM "{table_name}"
        WHERE "{primary_key}" = '{escaped_value}'
        LIMIT 1
    '''

    response = execute_sql(query)

    if not response.get("ok"):
        raise RuntimeError(
            response.get("error", "Unable to retrieve record")
        )

    return {
        "columns": response.get("columns", []),
        "rows": response.get("rows", []),
    }


def update_record(
    table_name,
    primary_key,
    primary_key_value,
    values,
):
    """Update a record identified by its primary key 
    using the supplied values."""
    assignments = []

    for column_name, value in values.items():

        escaped_column = column_name.replace(
            '"', '""'
        )

        if value is None:
            sql_value = "NULL"
        else:
            escaped_value = str(value).replace(
                "'", "''"
            )
            sql_value = f"'{escaped_value}'"

        assignments.append(
            f'"{escaped_column}" = {sql_value}'
        )

    if not assignments:
        raise RuntimeError(
            "No values to update"
        )

    escaped_pk = str(
        primary_key_value
    ).replace("'", "''")

    query = f'''
        UPDATE "{table_name}"
        SET {", ".join(assignments)}
        WHERE "{primary_key}" = '{escaped_pk}'
    '''

    response = execute_sql(query)

    if not response.get("ok"):
        raise RuntimeError(
            response.get("error", "Update failed")
        )

    return response


def delete_record(
    table_name,
    primary_key,
    primary_key_value,
):
    """Delete a record identified by its primary key."""
    escaped_pk = str(
        primary_key_value
    ).replace("'", "''")

    query = f'''
        DELETE FROM "{table_name}"
        WHERE "{primary_key}" = '{escaped_pk}'
    '''

    response = execute_sql(query)

    if not response.get("ok"):
        raise RuntimeError(
            response.get("error", "Delete failed")
        )

    return response


