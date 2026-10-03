#!/usr/bin/env python3

import os

from rsqlite import transport

from database import get_tables, browse_table, get_schema


IDENTITY_FILE = os.path.expanduser(
    "~/.reticulum/identities/rsqlite"
)

DESTINATION_HASH = "8393998345af43b99b3b618309174a29"


def print_rows(columns, rows):
    if columns:
        print(" | ".join(str(column) for column in columns))
    else:
        print("No columns.")

    print()
    print("-=")
    print()

    if rows:
        for row in rows:
            values = [
                str(value) if value is not None else "NULL"
                for value in row
            ]
            print(" | ".join(values))
    else:
        print("No records.")


def main():

    table_name = os.environ.get("var_table")
    action = os.environ.get("var_action")

    print("# rSQLite")
    print()

    print("`F58aDatabase Browser`f")
    print()

    print("-=")
    print()

    print("`F58aConnection`f")
    print()

    print("Server: rSQLite")
    print("Transport: Reticulum")

    print("Status: `F0a6connecting...`f")
    print()

    try:

        transport.connect(
            IDENTITY_FILE,
            DESTINATION_HASH,
        )

        print("Status: `F0a6connected`f")
        print()

        if table_name:

            if not table_name.replace("_", "").isalnum():
                print("`Ff00Invalid table name`f")
                return

            if not action:
                action = "browse"

            print(f"# {table_name}")
            print()

            print(
                f"`[Browse`:/page/rsqlite-gui.py"
                f"`table={table_name}|action=browse] "
                f"`[Schema`:/page/rsqlite-gui.py"
                f"`table={table_name}|action=schema]"
            )
            print()

            if action == "browse":

                data = browse_table(table_name)

                print("`F58aColumns`f")
                print()

                print_rows(
                    data["columns"],
                    data["rows"],
                )

            elif action == "schema":

                data = get_schema(table_name)

                print("`F58aTable Schema`f")
                print()

                print_rows(
                    data["columns"],
                    data["rows"],
                )

            else:

                print("`Ff00Unknown action`f")
                print()
                print(action)

            print()
            print("-=")
            print()

            print(
                "`[← Tables`:/page/rsqlite-gui.py]"
            )

        else:

            print("`F58aTables`f")
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

            print("`F58aDatabase`f")
            print()

            print("SQLite")
            print("Status: `F0a6connected`f")

    except Exception as e:

        print("`Ff00CONNECTION ERROR`f")
        print()

        print(type(e).__name__)
        print(str(e))

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
