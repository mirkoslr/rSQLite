#!/usr/bin/env python3

import os
from pathlib import Path

from rsqlite import config
from rsqlite import transport
from rsqlite import shell
from links import link

from database import (
    get_tables,
    count_records,
    browse_table,
    get_schema,
    insert_record,
    get_record,
    update_record,
    delete_record,
)

CONFIG_FILE = Path.home() / ".rsqlite" / "config" / "rsqlite-cli.conf"
RECORDS_PER_PAGE = 20

def print_rows(columns, rows):
    if columns:
        print(
            " | ".join(
                str(column)
                for column in columns
            )
        )
    else:
        print("No columns.")
    print()
    print("-=")
    print()
    if rows:
        for row in rows:
            values = [
                str(value)
                if value is not None
                else "NULL"
                for value in row
            ]
            print(
                " | ".join(values)
            )
    else:
        print("No records.")
def get_page_number():
    try:
        page = int(
            os.environ.get(
                "var_page",
                "1"
            )
        )
    except ValueError:
        page = 1
    return max(1, page)

def get_primary_key(schema_rows):
    primary_keys = []
    for row in schema_rows:
        column_name = row[1]
        primary_key = row[5]
        if primary_key:
            primary_keys.append(
                column_name
            )
    if len(primary_keys) != 1:
        return None
    return primary_keys[0]

def get_submitted_fields(schema_rows):
    values = {}
    for row in schema_rows:
        column_name = row[1]
        primary_key = row[5]
        column_type = (
            row[2] or ""
        ).upper()
        # Skip automatically generated
        # INTEGER PRIMARY KEY columns.
        if (
            primary_key
            and column_type == "INTEGER"
        ):
            continue
        field_name = (
            f"field_{column_name}"
        )
        if field_name in os.environ:
            values[column_name] = (
                os.environ[field_name]
            )
    return values

def print_insert_form(
    table_name,
    schema_rows,
):
    print("`F58aInsert Record`f")
    print()
    for row in schema_rows:
        column_name = row[1]
        column_type = row[2] or ""
        not_null = row[3]
        default_value = row[4]
        primary_key = row[5]
        # Skip automatically generated
        # INTEGER PRIMARY KEY columns.
        if (
            primary_key
            and column_type.upper() == "INTEGER"
        ):
            continue
        print(
            f"{column_name} "
            f"({column_type})"
        )
        print(
            f"`B444`<40|{column_name}`>`b"
        )
        if not_null:
            print("Required")
        elif default_value is not None:
            print(
                f"Default: {default_value}"
            )
        print()

    print(link(
        "Insert",
        "/page/rsqlite-gui.py",
        [
            ("table", table_name),
            ("action", "insert"),
            ("server", os.environ.get("var_server")),
            "*",
        ],
    ))

def print_update_form(
    table_name,
    schema_rows,
    record,
    primary_key,
    primary_key_value,
):
    print("`F58aUpdate Record`f")
    print()
    for index, row in enumerate(
        schema_rows
    ):
        column_name = row[1]
        column_type = row[2] or ""
        not_null = row[3]
        # Primary key is not editable.
        if column_name == primary_key:
            continue
        current_value = record[index]
        print(
            f"{column_name} "
            f"({column_type})"
        )
        print(
            f"`B444`<40|{column_name}`>`b"
        )
        if current_value is not None:
            print(
                f"Current value: "
                f"{current_value}"
            )
        if not_null:
            print("Required")
        print()

    print(link(
        "Update",
        "/page/rsqlite-gui.py",
        [
            ("table", table_name),
            ("action", "update"),
            ("pk", primary_key_value),
            ("server", os.environ.get("var_server")),
            "*",
        ],
    ))

def print_browse_rows(
    table_name,
    columns,
    rows,
    primary_key,
):
    if columns:
        print(
            " | ".join(
                str(column)
                for column in columns
            )
        )
    print()
    print("-=")
    print()
    if not rows:
        print("No records.")
        return
    try:
        primary_key_index = (
            columns.index(
                primary_key
            )
        )
    except ValueError:
        primary_key_index = None
    for row in rows:
        values = [
            str(value)
            if value is not None
            else "NULL"
            for value in row
        ]
        print(
            " | ".join(values)
        )
        if primary_key_index is not None:
            primary_key_value = (
                row[primary_key_index]
            )

            print(link(
                "Update",
                "/page/rsqlite-gui.py",
                [
                    ("table", table_name),
                    ("action", "update"),
                    ("pk", primary_key_value),
                    ("server", os.environ.get("var_server")),
                ],
                color="FEA4",
            ), end=" | ")

            print(link(
                "Delete",
                "/page/rsqlite-gui.py",
                [
                    ("table", table_name),
                    ("action", "delete"),
                    ("pk", primary_key_value),
                    ("server", os.environ.get("var_server")),
                ],
                color="FD55",
            ))
        print()

def get_server_param():
    server_index = os.environ.get("var_server")
    return f"|server={server_index}"

def print_server_selection(servers):
    print()
    print("`F58aSelect Server`f")
    print("`F58a_____________`f")
    print()
    print("Configured servers")
    print()

    for index, server in enumerate(servers):
        name = server["name"]
        destination = server["destination_hash"]

        print(link(
            f"→ {name}",
            "/page/rsqlite-gui.py",
            [("server", index)],
            color="FEA4",
        ))

        print(f"  Destination: {destination}")
        print()

def get_connection():
    identity_file, servers = config.load_config(
        CONFIG_FILE
    )

    if not servers:
        raise RuntimeError(
            "No rSQLite servers configured"
        )

    server_index = os.environ.get("var_server")

    if server_index is None:
        print_server_selection(servers)
        return None

    try:
        server_index = int(server_index)
    except ValueError:
        raise RuntimeError(
            "Invalid server selection"
        )

    if server_index < 0 or server_index >= len(servers):
        raise RuntimeError(
            "Invalid server selection"
        )

    server = servers[server_index]

    transport.connect(
        identity_file,
        server["destination_hash"],
    )

    return server_index, server


def main():
    table_name = os.environ.get(
        "var_table"
    )
    action = os.environ.get(
        "var_action"
    )
    page = get_page_number()
    print("# rSQLite")
    print()
    print(
        "`F58aDatabase Browser`f"
    )
    print()
    print("-=")
    print()
    print("`F58aConnection`f")
    print("`F58a__________`f")
    print()
    print("Server: rSQLite")
    print("Transport: Reticulum")
    
    try:
        connection = get_connection()

        if connection is None:
            return

        server_index, server = connection
        server_param = f"|server={server_index}"
        print(
            "Status: "
            "`F0a6connected`f"
        )
        print()

        if action == "sql":
            submitted_query = os.environ.get("field_sql_query")

            if submitted_query:
                result = shell.execute_and_render(submitted_query)
                print(result)

            print("`F58aSQL SHELL`f")
            print()

            print("SQL execution interface")
            print()

            print(
                "`B444`<60|sql_query`>`b"
            )

            print()

            print(link(
                "Execute",
                "/page/rsqlite-gui.py",
                [
                    "sql_query",
                    ("action", "sql"),
                    ("server", server_index),
                ],
            ))

            print()

            print(link(
                "← Tables",
                "/page/rsqlite-gui.py",
                [("server", server_index)],
            ))

        elif table_name:
            if not table_name.replace(
                "_", ""
            ).isalnum():
                print(
                    "`Ff00Invalid table name`f"
                )
                return
            if not action:
                action = "browse"
            print(
                f"# {table_name}"
            )
            print()

            print("| ", end="")
            print(link(
                "Browse",
                "/page/rsqlite-gui.py",
                [("table", table_name), ("action", "browse"), ("server", server_index)],
                color="F58A",
            ), end=" | ")

            print(link(
                "Schema",
                "/page/rsqlite-gui.py",
                [("table", table_name), ("action", "schema"), ("server", server_index)],
                color="FA8F",
            ), end=" | ")

            print(link(
                "Insert",
                "/page/rsqlite-gui.py",
                [("table", table_name), ("action", "insert"), ("server", server_index)],
                color="FEC7",
            ), end=" | ")
            print()
            print()

            if action == "browse":
                schema = get_schema(
                    table_name
                )
                primary_key = (
                    get_primary_key(
                        schema["rows"]
                    )
                )
                total = count_records(
                    table_name
                )
                total_records = 0
                if total["rows"]:
                    total_records = int(
                        total["rows"][0][0]
                    )
                total_pages = max(
                    1,
                    (
                        total_records
                        + RECORDS_PER_PAGE
                        - 1
                    )
                    // RECORDS_PER_PAGE
                )
                if page > total_pages:
                    page = total_pages
                offset = (
                    page - 1
                ) * RECORDS_PER_PAGE
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
                    print_rows(
                        data["columns"],
                        data["rows"],
                    )
                print()
                print(
                    f"Page {page} / "
                    f"{total_pages}"
                    f"  ({total_records} records)"
                )
                if page > 1:
                    print()
                    print(link(
                        "← Back",
                        "/page/rsqlite-gui.py",
                        [("table", table_name), ("action", "browse"), ("page", page - 1), ("server", server_index)],
                    ))
                if page < total_pages:
                    print()
                    print(link(
                        "Next →",
                        "/page/rsqlite-gui.py",
                        [("table", table_name), ("action", "browse"), ("page", page + 1), ("server", server_index)],
                    ))
            elif action == "schema":
                data = get_schema(
                    table_name
                )
                print("Table Schema")
                print()
                print_rows(
                    data["columns"],
                    data["rows"],
                )
            elif action == "insert":
                schema = get_schema(
                    table_name
                )
                schema_rows = schema[
                    "rows"
                ]
                submitted_fields = (
                    get_submitted_fields(
                        schema_rows
                    )
                )
                if submitted_fields:
                    insert_record(
                        table_name,
                        submitted_fields,
                    )
                    print(
                        "`F0a6Record inserted "
                        "successfully.`f"
                    )
                    print()
                    print(link(
                        "← Browse",
                        "/page/rsqlite-gui.py",
                        [("table", table_name), ("action", "browse"), ("page", 1), ("server", server_index)],
                    ))
                else:
                    print_insert_form(
                        table_name,
                        schema_rows,
                    )
            elif action == "update":
                schema = get_schema(
                    table_name
                )
                schema_rows = schema[
                    "rows"
                ]
                primary_key = (
                    get_primary_key(
                        schema_rows
                    )
                )
                if not primary_key:
                    raise RuntimeError(
                        "Update requires "
                        "a single primary key"
                    )
                primary_key_value = (
                    os.environ.get(
                        "var_pk"
                    )
                )
                if primary_key_value is None:
                    print(
                        "`Ff00Missing primary "
                        "key`f"
                    )
                else:
                    record_data = (
                        get_record(
                            table_name,
                            primary_key,
                            primary_key_value,
                        )
                    )
                    if not record_data[
                        "rows"
                    ]:
                        print(
                            "`Ff00Record not found`f"
                        )
                    else:
                        record = (
                            record_data[
                                "rows"
                            ][0]
                        )
                        submitted_fields = (
                            get_submitted_fields(
                                schema_rows
                            )
                        )
                        if submitted_fields:
                            update_record(
                                table_name,
                                primary_key,
                                primary_key_value,
                                submitted_fields,
                            )
                            print(
                                "`F0a6Record updated "
                                "successfully.`f"
                            )
                            print()
                            print(link(
                                "← Browse",
                                "/page/rsqlite-gui.py",
                                [("table", table_name), ("action", "browse"), ("page", 1), ("server", server_index)],
                            ))
                        else:
                            print_update_form(
                                table_name,
                                schema_rows,
                                record,
                                primary_key,
                                primary_key_value,
                            )
            elif action == "delete":
                schema = get_schema(
                    table_name
                )
                schema_rows = schema[
                    "rows"
                ]
                primary_key = (
                    get_primary_key(
                        schema_rows
                    )
                )
                if not primary_key:
                    raise RuntimeError(
                        "Delete requires "
                        "a single primary key"
                    )
                primary_key_value = (
                    os.environ.get(
                        "var_pk"
                    )
                )
                if primary_key_value is None:
                    print(
                        "`Ff00Missing primary "
                        "key`f"
                    )
                else:
                    record_data = (
                        get_record(
                            table_name,
                            primary_key,
                            primary_key_value,
                        )
                    )
                    if not record_data[
                        "rows"
                    ]:
                        print(
                            "`Ff00Record not found`f"
                        )
                    else:
                        record = (
                            record_data[
                                "rows"
                            ][0]
                        )
                        confirm = (
                            os.environ.get(
                                "var_confirm"
                            )
                        )
                        if confirm == "yes":
                            delete_record(
                                table_name,
                                primary_key,
                                primary_key_value,
                            )
                            print(
                                "`F0a6Record deleted "
                                "successfully.`f"
                            )
                            print()
                            print(link(
                                "← Browse",
                                "/page/rsqlite-gui.py",
                                [("table", table_name), ("action", "browse"), ("page", 1), ("server", server_index)],
                            ))
                        else:
                            print(
                                "`F58aDelete Record`f"
                            )
                            print()
                            print(
                                "Are you sure you "
                                "want to delete "
                                "this record?"
                            )
                            print()
                            for column, value in zip(
                                record_data[
                                    "columns"
                                ],
                                record,
                            ):
                                display_value = (
                                    "NULL"
                                    if value is None
                                    else str(value)
                                )
                                print(
                                    f"{column}: "
                                    f"{display_value}"
                                )
                            print()
                            print(link(
                                "Confirm Delete",
                                "/page/rsqlite-gui.py",
                                [("table", table_name), ("action", "delete"), ("pk", primary_key_value), ("server", server_index), ("confirm", "yes")],
                            ))
                            print()
                            print(link(
                                "Cancel",
                                "/page/rsqlite-gui.py",
                                [("table", table_name), ("action", "browse"), ("page", 1), ("server", server_index)],
                            ))
            else:
                print(
                    "`Ff00Unknown action`f"
                )
                print()
                print(action)
            print()
            print("-=")
            print()
            print(link(
                "← Tables",
                "/page/rsqlite-gui.py",
                [("server", server_index)],
            ))
        else:
            print(
                "`F58aTables`f"
            )
            print("`F58a______`f")
            print()
            tables = get_tables()
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
       
    except Exception as e:
        print(
            "`Ff00CONNECTION ERROR`f"
        )
        print()
        print(
            type(e).__name__
        )
        print(
            str(e)
        )
    finally:
        transport.close()
    print()
    print("-=")

    print(link(
        "Refresh",
        "/page/rsqlite-gui.py",
        color="F39F"
        ))
if __name__ == "__main__":
    main()
