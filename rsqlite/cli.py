#!/usr/bin/env python3

import argparse
import readline

from rsqlite import config
from rsqlite import formatter
from rsqlite import transport
from rsqlite import shell

from pathlib import Path

dispatch_command = shell.dispatch_command
execute_command = shell.execute_command

CONFIG_FILE = Path.home() / ".rsqlite" / "config" / "rsqlite-cli.conf"
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
            result = execute_command(cmd, arg, servers)
            if result is not None:
                if isinstance(result, str):
                    print(result)
                else:
                    print(formatter.render(result))
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
    