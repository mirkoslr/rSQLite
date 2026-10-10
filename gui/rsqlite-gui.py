#!/usr/bin/env python3

import os

from pathlib import Path

from rsqlite import config

from rsqlite import transport


from links import link

from handlers import (
    handle_schema,
    handle_sql,
    handle_insert,
    handle_update,
    handle_delete,
    handle_browse,
    handle_tables,
    handle_table_action,
    get_primary_key,
)

from views import (
    print_rows,
    print_insert_form,
    print_update_form,
    print_browse_rows,
    print_server_selection,
)

from database import (

    get_tables,

    count_records,

    browse_table,

    get_schema,





)

CONFIG_FILE = Path.home() / ".rsqlite" / "config" / "rsqlite-cli.conf"

RECORDS_PER_PAGE = 20


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

def get_server_param():

    server_index = os.environ.get("var_server")

    return f"|server={server_index}"


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

    table_name = os.environ.get("var_table")
    action = os.environ.get("var_action")
    page = get_page_number()

    print("# rSQLite")
    print()
    print("`F58aDatabase Browser`f")
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

            handle_sql(server_index)

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

            handle_table_action(
                action,
                table_name,
                page,
                server_index,
            )
            print()
            print("-=")
            print()
            
            print(link(

                "← Tables",

                "/page/rsqlite-gui.py",

                [("server", server_index)],

            ))

        else:
            tables = get_tables()
            handle_tables(tables, server_index)

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

