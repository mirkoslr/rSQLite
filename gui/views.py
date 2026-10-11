import os
from links import link


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

        color="FEA4",

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

        color="FEA4",

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

def print_server_selection(servers):
    """Display the servers from the client configuration."""
    print()
    print("`F58aSelect Server`f")
    print("`F58a_____________`f")

    print()
    print("Configured servers")
    print()

    for index, server in enumerate(servers):
        name = server["name"]
        destination = server["destination_hash"]
        print(link(f"→ {name}", "/page/rsqlite-gui.py",
            [("server", index)],color="FEA4",))
        
        print(f"  Destination: {destination}")
        print()
