#!/usr/bin/env python3
"""
rSQLite command-line interface.

Responsibilities:
- Parse command-line arguments
- Configure and connect to the selected server
- Execute SQL commands and interactive queries
- Display query results
- Export query results to files
- Close the transport connection
"""

import argparse
import json

import RNS

try:
    import readline  # noqa: F401 - enables line editing where available
except ImportError:  # readline is unavailable in some Python builds, notably Windows
    pass

from pathlib import Path
from datetime import date

from rsqlite import config
from rsqlite import formatter
from rsqlite import exporter
from rsqlite import transport
from rsqlite import shell
from rsqlite.identity import prepare_identity
from rsqlite.initializer import initialize_environment


dispatch_command = shell.dispatch_command
execute_command = shell.execute_command

CONFIG_FILE = Path.home() / ".rsqlite" / "config" / "rsqlite-cli.conf"
VERSION = "0.1.0"

def show_servers(servers):
    """Display the configured servers and their destination hashes."""
    print()
    print("Configured servers")
    print("------------------")

    for index, server in enumerate(servers, start=1):
        print(f"{index}) {server['name']}")
        print(f"   Destination: {server['destination_hash']}")


def choose_server(servers):
    """Let the user select a configured server and return it."""
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
    """Run the interactive SQL prompt and execute queries."""
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
    """Parse command-line arguments and run the rSQLite client.
    Handle identity display, database export and interactive SQL mode.
    """
    parser = argparse.ArgumentParser(description="rSQLite client")

    parser.add_argument(
        "-c",
        "--config",
        default=CONFIG_FILE,
        help="Configuration file"
    )

    parser.add_argument(
        "--init",
        action="store_true",
        help="Create the default rSQLite environment and exit",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable Reticulum debug logging"
    )

    parser.add_argument(
        "--print-identity",
        action="store_true",
        help="Print client identity information and exit",
    )

    parser.add_argument(
        "-e", "--export",
        metavar="TABLE",
        help="Export a database table"
    )

    parser.add_argument(
        "-f", "--format",
        choices=["csv", "json", "txt"],
        default="csv",
        help="Export format (default: csv)"
    )

    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="Output file path"
    )

    args = parser.parse_args()

    if args.init:
        try:
            initialize_environment()
        except FileExistsError as exc:
            parser.exit(1, f"Initialization stopped. {exc}\n")
        except Exception as exc:
            parser.exit(1, f"Initialization failed: {exc}\n")
        return

    # Quiet by default, verbose only when debugging.
    transport.set_debug(args.debug)

    identity_file, servers = config.load_config(args.config)

    if args.print_identity:
        identity = prepare_identity(identity_file)
        print("rSQLite Identity")
        print("----------------")
        print(f"Identity file : {identity_file}")
        print(f"Identity hash : {RNS.prettyhexrep(identity.hash)}")
        return

    print()
    print("rSQLite")
    print("-------")
    print(f"Identity : {identity_file}")

    server = choose_server(servers)

    print()
    print(f"Connected server   : {server['name']}")
    print(f"Destination hash   : {server['destination_hash']}")
    print()

    try:
        transport.connect(identity_file, server["destination_hash"])
        
        if args.export:
            query = f'SELECT * FROM "{args.export.replace(chr(34), chr(34) * 2)}"'
            response = transport.execute(query)

            result = json.loads(response) if isinstance(response, str) else response

            if not result.get("ok", False):
                print(formatter.render(result))
                return

            output_file = args.output or (
                f"{args.export}.{date.today().strftime('%d.%m.%y')}.{args.format}"
            )

            exporters = {
                "csv": exporter.export_csv,
                "json": exporter.export_json,
                "txt": exporter.export_txt,
            }

            exporters[args.format](result, output_file)
            print(f"Export completed: {output_file}")
            return

        sql_prompt(servers)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        transport.close()

if __name__ == "__main__":
    main()
    