#!/usr/bin/env python3

import argparse
import readline

from rsqlite import config
from rsqlite import formatter
from rsqlite import transport

CONFIG_FILE = "rsqlite-cli.conf"
VERSION = "0.1.0"


def show_servers(servers):
    print()
    print("Configured servers")
    print("------------------")

    for index, server in enumerate(servers, start=1):
        print(f"{index}) {server['name']}")
        print(f"   Destination: {server['destination_hash']}")


def choose_server(servers):
    show_servers(servers)

    while True:
        try:
            choice = int(input("\nSelect server: "))

            if 1 <= choice <= len(servers):
                return servers[choice - 1]

        except ValueError:
            pass

        print("Invalid selection.")


def dispatch_command(line):
    parts = line.split()

    if not parts:
        return None, None

    if parts[0] in (".quit", ".exit"):
        return "quit", None

    if parts[0] == ".help":
        return "help", None

    if parts[0] == ".tables":
        return "tables", None

    if parts[0] == ".schema":
        arg = parts[1] if len(parts) > 1 else None
        return "schema", arg

    if parts[0] == ".indexes":
        return "indexes", None

    if parts[0] == ".databases":
        return "databases", None

    if parts[0] == ".version":
        return "version", None

    if parts[0] == ".db":
        return "databases_configured", None

    return None, None


def execute_command(cmd, arg, servers):

    if cmd == "help":
        print("""Commands:
  .help       Show this help
  .tables     List tables
  .schema     Show table schema
  .indexes    List indexes
  .databases  List databases
  .db         List configured servers
  .version    Show rSQL version
  .quit       Exit rSQL
  .exit       Exit rSQL""")
        return

    elif cmd == "databases_configured":
        show_servers(servers)
        return

    elif cmd == "tables":
        query = """
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
"""

    elif cmd == "schema":
        query = """
SELECT name, sql
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
"""

    elif cmd == "indexes":
        query = """
SELECT name
FROM sqlite_master
WHERE type = 'index'
ORDER BY name;
"""

    elif cmd == "databases":
        query = """
PRAGMA database_list;
"""

    elif cmd == "version":
        print(f"rSQLite version {VERSION}")
        query = """
SELECT sqlite_version();
"""

    try:
        response = transport.execute(query)
        print(formatter.render(response))
    except RuntimeError as e:
        print(f"Error: {e}")


def sql_prompt(servers):
    lines = []

    while True:
        try:
            prompt = "rSQL> " if not lines else "...   "
            line = input(prompt)

        except (EOFError, KeyboardInterrupt):
            print()
            break

        line = line.strip()

        cmd, arg = dispatch_command(line)

        if cmd == "quit":
            break

        if cmd:
            execute_command(cmd, arg, servers)
            continue

        # Empty line: execute a single-line query.
        if not line and not lines:
            continue

        # Empty line after starting a query: execute it.
        if not line and lines:
            query = "\n".join(lines)
            lines = []

            try:
                response = transport.execute(query)
                print(formatter.render(response))
            except Exception as e:
                print(f"Error: {e}")

            continue

        lines.append(line)

        # Semicolon terminates the SQL statement.
        if line.endswith(";"):
            query = "\n".join(lines)
            lines = []

            try:
                response = transport.execute(query)
                print(formatter.render(response))
            except Exception as e:
                print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="rSQLite client")

    parser.add_argument(
        "-c",
        "--config",
        default=CONFIG_FILE,
        help="Configuration file"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable Reticulum debug logging"
    )

    args = parser.parse_args()

    # Quiet by default, verbose only when debugging.
    transport.set_debug(args.debug)

    identity_file, servers = config.load_config(args.config)

    print()
    print("rSQLite")
    print("-------")
    print(f"Identity : {identity_file}")

    server = choose_server(servers)

    print()
    print(f"Connected server   : {server['name']}")
    print(f"Destination hash   : {server['destination_hash']}")
    print()

    transport.connect(identity_file, server["destination_hash"])

    try:
        sql_prompt(servers)
    finally:
        transport.close()


if __name__ == "__main__":
    main()
    