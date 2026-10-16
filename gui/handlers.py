"""
Handle database operations and user interactions for the rSQLite NomadNet GUI.

Responsibilities:
    - Identify a table's primary key and validate submitted form fields.
    - Read submitted form values from the environment and check required fields.
    - Display table schemas and provide an interface for executing SQL queries.
    - Handle record insertion, updating and deletion, including validation,
      error reporting and operation confirmations.
    - Browse table records with pagination and provide navigation between pages.
    - Display available database tables and route user requests to the
      appropriate handler based on the selected action.
    - Coordinate database operations through the database module and display
      results and interactive navigation links through the views and links modules.
"""

import os

from rsqlite import shell
from database import count_records, browse_table
from links import link
from rsqlite.constants import RECORDS_PER_PAGE

from database import (
    get_schema,
    insert_record,
    get_record,
    update_record,
    delete_record,
)
from views import (
    print_rows,
    print_insert_form,
    print_update_form,
    print_browse_rows,
)

def get_primary_key(schema_rows):
    """Return the name of the primary key 
    if it consists of a single column."""
    primary_keys = []

    for row in schema_rows:
        column_name = row[1]
        primary_key = row[5]
        if primary_key:
            primary_keys.append(column_name)
    if len(primary_keys) != 1:
        return None
    return primary_keys[0]


def get_submitted_fields(schema_rows):
    """Collect submitted form values, 
    excluding automatically generated integer primary keys."""
    values = {}

    for row in schema_rows:
        column_name = row[1]
        primary_key = row[5]
        column_type = (row[2] or "").upper()
        # Skip automatically generated INTEGER PRIMARY KEY columns.
        if primary_key and column_type == "INTEGER":
            continue
        field_name = f"field_{column_name}"
        if field_name in os.environ:
            values[column_name] = os.environ[field_name]
    return values


def validate_fields(schema_rows, submitted_fields, primary_key=None):
    """Identify missing values in required fields that have no default."""
    errors = []

    for row in schema_rows:
        column_name = row[1]
        not_null = row[3]
        default_value = row[4]
        is_primary_key = row[5]
        if column_name == primary_key:
            continue
        if is_primary_key and (row[2] or "").upper() == "INTEGER":
            continue
        value = submitted_fields.get(column_name)
        if not_null and default_value is None:
            if value is None or not value.strip():
                errors.append(column_name)
    return errors


def handle_schema(table_name):
    """Display the schema of the specified database table."""
    data = get_schema(table_name)

    print("Table Schema")
    print()
    print_rows(data["columns"], data["rows"])


def handle_sql(server_index):
    submitted_query = os.environ.get("field_sql_query")
    if submitted_query:
        result = shell.execute_and_render(submitted_query)
        print(result)
    print("`F58aSQL SHELL`f")
    print()
    print("SQL execution interface")
    print()
    print("`B444`<60|sql_query`>`b")
    print()
    print(link(
        "Execute",
        "/page/rsqlite-gui.py",
        ["sql_query", ("action", "sql"), ("server", server_index)],
        color="FEA4",
    ))
    print()
    print(link(
        "← Tables",
        "/page/rsqlite-gui.py",
        [("server", server_index)],
    ))


def handle_insert(table_name, server_index):
    """Validate submitted fields, insert a record or 
    display the insertion form."""
    schema = get_schema(table_name)
    schema_rows = schema["rows"]
    submitted_fields = get_submitted_fields(schema_rows)
    if submitted_fields:
        errors = validate_fields(schema_rows, submitted_fields)
        if errors:
            print("`Ff00Required fields missing:`f")
            print(", ".join(errors))
            print()
            print_insert_form(table_name, schema_rows)
        else:
            insert_record(table_name, submitted_fields)
            print("`F0a6Record inserted successfully.`f")
            print()
            print(link(
                "← Browse",
                "/page/rsqlite-gui.py",
                [("table", table_name), ("action", "browse"), ("page", 1), ("server", server_index)],
            ))
    else:
        print_insert_form(table_name, schema_rows)


def handle_update(table_name, server_index):
    """Load a record and update it after validating the submitted fields."""
    schema = get_schema(table_name)
    schema_rows = schema["rows"]
    primary_key = get_primary_key(schema_rows)
    if not primary_key:
        raise RuntimeError("Update requires a single primary key")
    primary_key_value = os.environ.get("var_pk")
    if primary_key_value is None:
        print("`Ff00Missing primary key`f")
        return
    record_data = get_record(table_name, primary_key, primary_key_value)
    if not record_data["rows"]:
        print("`Ff00Record not found`f")
        return
    record = record_data["rows"][0]
    submitted_fields = get_submitted_fields(schema_rows)
    if submitted_fields:
        errors = validate_fields(
            schema_rows,
            submitted_fields,
            primary_key=primary_key,
        )
        if errors:
            print("`Ff00Required fields missing:`f")
            print(", ".join(errors))
            print()
            print_update_form(
                table_name, schema_rows, record, primary_key, primary_key_value
            )
        else:
            update_record(
                table_name, primary_key, primary_key_value, submitted_fields
            )
            print("`F0a6Record updated successfully.`f")
            print()
            print(link(
                "← Browse",
                "/page/rsqlite-gui.py",
                [("table", table_name), ("action", "browse"), ("page", 1), ("server", server_index)],
            ))
    else:
        print_update_form(
            table_name, schema_rows, record, primary_key, primary_key_value
        )


def handle_delete(table_name, server_index):
    """Request deletion confirmation and delete the selected record 
    when confirmed."""
    schema = get_schema(table_name)
    schema_rows = schema["rows"]
    primary_key = get_primary_key(schema_rows)
    if not primary_key:
        raise RuntimeError("Delete requires a single primary key")
    primary_key_value = os.environ.get("var_pk")
    if primary_key_value is None:
        print("`Ff00Missing primary key`f")
        return
    record_data = get_record(table_name, primary_key, primary_key_value)
    if not record_data["rows"]:
        print("`Ff00Record not found`f")
        return
    record = record_data["rows"][0]
    confirm = os.environ.get("var_confirm")
    if confirm == "yes":
        delete_record(table_name, primary_key, primary_key_value)
        print("`F0a6Record deleted successfully.`f")
        print()
        print(link(
            "← Browse",
            "/page/rsqlite-gui.py",
            [("table", table_name), ("action", "browse"), ("page", 1), ("server", server_index)],
        ))
    else:
        print("`F58aDelete Record`f")
        print()
        print("Are you sure you want to delete this record?")
        print()
        for column, value in zip(record_data["columns"], record):
            display_value = "NULL" if value is None else str(value)
            print(f"{column}: {display_value}")
        print()
        print(link(
            "Confirm Delete",
            "/page/rsqlite-gui.py",
            [("table", table_name), ("action", "delete"), ("pk", primary_key_value), ("server", server_index), ("confirm", "yes")],color="FEA4",
        ))
        print()
        print(link(
            "Cancel",
            "/page/rsqlite-gui.py",
            [("table", table_name), ("action", "browse"), ("page", 1), ("server", server_index)],
        ))

def handle_browse(table_name, page, server_index):
    """Display a paginated view of table records with navigation links."""
    schema = get_schema(table_name)
    primary_key = get_primary_key(schema["rows"])

    total = count_records(table_name)
    total_records = 0

    if total["rows"]:
        total_records = int(total["rows"][0][0])

    total_pages = max(
        1,
        (total_records + RECORDS_PER_PAGE - 1) // RECORDS_PER_PAGE,
    )

    page = min(page, total_pages)
    offset = (page - 1) * RECORDS_PER_PAGE

    data = browse_table(
        table_name,
        limit=RECORDS_PER_PAGE,
        offset=offset,
    )

    print("Columns")
    print()

    if primary_key:
        print_browse_rows(
            table_name,
            data["columns"],
            data["rows"],
            primary_key,
        )
    else:
        print_rows(data["columns"], data["rows"])

    print()
    print(
        f"Page {page} / {total_pages}"
        f"  ({total_records} records)"
    )

    if page > 1:
        print()
        print(link(
            "← Back",
            "/page/rsqlite-gui.py",
            [
                ("table", table_name),
                ("action", "browse"),
                ("page", page - 1),
                ("server", server_index),
            ],
        ))

    if page < total_pages:
        print()
        print(link(
            "Next →",
            "/page/rsqlite-gui.py",
            [
                ("table", table_name),
                ("action", "browse"),
                ("page", page + 1),
                ("server", server_index),
            ],
        ))

def handle_tables(tables, server_index):
    """Display database tables and provide a link to the SQL shell."""
    print("`F58aTables`f")
    print("`F58a______`f")
    print()

    if tables:
        for table_name in tables:
            print(link(
                table_name,
                "/page/rsqlite-gui.py",
                [("table", table_name), ("server", server_index)],
            ))
    else:
        print("No tables.")

    print()
    print("`FEA4[ `f", end="")
    print(link(
        "SQL Shell",
        "/page/rsqlite-gui.py",
        [("action", "sql"), ("server", server_index)],
        color="FEA4",
    ), end="")
    print("`FEA4 ]`f")

def handle_table_action(action, table_name, page, server_index):
    """Dispatch the requested table action to its corresponding handler."""
    actions = {
        "browse": lambda: handle_browse(
            table_name, page, server_index
        ),
        "schema": lambda: handle_schema(table_name),
        "insert": lambda: handle_insert(
            table_name, server_index
        ),
        "update": lambda: handle_update(
            table_name, server_index
        ),
        "delete": lambda: handle_delete(
            table_name, server_index
        ),
    }

    handler = actions.get(action)

    if handler:
        handler()
    else:
        print("`Ff00Unknown action`f")
        print()
        print(action)

