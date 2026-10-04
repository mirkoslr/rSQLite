#!/usr/bin/env python3

import os

from rsqlite import transport

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


IDENTITY_FILE = os.path.expanduser(
    "~/.reticulum/identities/rsqlite"
)

DESTINATION_HASH = "8393998345af43b99b3b618309174a29"

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

    print(
        f"`[Insert`:/page/rsqlite-gui.py"
        f"`table={table_name}"
        f"|action=insert|*]`"
    )


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

    print(
        f"`[Update`:/page/rsqlite-gui.py"
        f"`table={table_name}"
        f"|action=update"
        f"|pk={primary_key_value}"
        f"|*]`"
    )


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

            print(
                f"`[Update`:/page/rsqlite-gui.py"
                f"`table={table_name}"
                f"|action=update"
                f"|pk={primary_key_value}] "
                f"`[Delete`:/page/rsqlite-gui.py"
                f"`table={table_name}"
                f"|action=delete"
                f"|pk={primary_key_value}]`"
            )

        print()


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
    print()

    print("Server: rSQLite")
    print("Transport: Reticulum")

    print(
        "Status: "
        "`F0a6connecting...`f"
    )
    print()

    try:

        transport.connect(
            IDENTITY_FILE,
            DESTINATION_HASH,
        )

        print(
            "Status: "
            "`F0a6connected`f"
        )
        print()

        if table_name:

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

            print(
                f"`[Browse`:/page/rsqlite-gui.py"
                f"`table={table_name}"
                f"|action=browse] "
                f"`[Schema`:/page/rsqlite-gui.py"
                f"`table={table_name}"
                f"|action=schema] "
                f"`[Insert`:/page/rsqlite-gui.py"
                f"`table={table_name}"
                f"|action=insert] "
                f"`[Update`:/page/rsqlite-gui.py"
                f"`table={table_name}"
                f"|action=browse]"
            )

            print()

            # ---------------------------------
            # BROWSE
            # ---------------------------------

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

                print(
                    "`F58aColumns`f"
                )
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

                    print(
                        f"`[← Back`:/page/rsqlite-gui.py"
                        f"`table={table_name}"
                        f"|action=browse"
                        f"|page={page - 1}]"
                    )

                if page < total_pages:

                    print()

                    print(
                        f"`[Next →`:/page/rsqlite-gui.py"
                        f"`table={table_name}"
                        f"|action=browse"
                        f"|page={page + 1}]"
                    )

            # ---------------------------------
            # SCHEMA
            # ---------------------------------

            elif action == "schema":

                data = get_schema(
                    table_name
                )

                print(
                    "`F58aTable Schema`f"
                )
                print()

                print_rows(
                    data["columns"],
                    data["rows"],
                )

            # ---------------------------------
            # INSERT
            # ---------------------------------

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

                    print(
                        f"`[← Browse`:/page/rsqlite-gui.py"
                        f"`table={table_name}"
                        f"|action=browse"
                        f"|page=1]"
                    )

                else:

                    print_insert_form(
                        table_name,
                        schema_rows,
                    )

            # ---------------------------------
            # UPDATE
            # ---------------------------------

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

                            print(
                                f"`[← Browse`:/page/rsqlite-gui.py"
                                f"`table={table_name}"
                                f"|action=browse"
                                f"|page=1]"
                            )

                        else:

                            print_update_form(
                                table_name,
                                schema_rows,
                                record,
                                primary_key,
                                primary_key_value,
                            )

            # ---------------------------------
            # DELETE
            # ---------------------------------

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

                            print(
                                f"`[← Browse`:/page/rsqlite-gui.py"
                                f"`table={table_name}"
                                f"|action=browse"
                                f"|page=1]"
                            )

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

                            print(
                                f"`[Confirm Delete`:"
                                f"/page/rsqlite-gui.py"
                                f"`table={table_name}"
                                f"|action=delete"
                                f"|pk={primary_key_value}"
                                f"|confirm=yes]`"
                            )

                            print()

                            print(
                                f"`[Cancel`:"
                                f"/page/rsqlite-gui.py"
                                f"`table={table_name}"
                                f"|action=browse"
                                f"|page=1]`"
                            )

            # ---------------------------------
            # UNKNOWN ACTION
            # ---------------------------------

            else:

                print(
                    "`Ff00Unknown action`f"
                )

                print()
                print(action)

            print()
            print("-=")
            print()

            print(
                "`[← Tables`:/page/rsqlite-gui.py]"
            )

        else:

            # ---------------------------------
            # TABLE LIST
            # ---------------------------------

            print(
                "`F58aTables`f"
            )
            print()

            tables = get_tables()

            if tables:

                for table_name in tables:

                    print(
                        f"`[{table_name}`"
                        f":/page/rsqlite-gui.py"
                        f"`table={table_name}]"
                    )

            else:

                print("No tables.")

            print()
            print("-=")
            print()

            print(
                "`F58aDatabase`f"
            )
            print()

            print("SQLite")

            print(
                "Status: "
                "`F0a6connected`f"
            )

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
    print()

    print(
        "`F08f`_`!`"
        "[Refresh`:/page/rsqlite-gui.py]"
        "`!`_`f"
    )


if __name__ == "__main__":
    main()
    
