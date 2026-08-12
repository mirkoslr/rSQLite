#!/usr/bin/env python3

import argparse
import configparser
import pathlib
import sys

import RNS
import formatter
import transport

CONFIG_FILE = "rsqlite.conf"


def load_config(filename):
    config = configparser.ConfigParser()

    if not pathlib.Path(filename).exists():
        print(f"Configuration file '{filename}' not found.")
        sys.exit(1)

    config.read(filename)

    if "identity" not in config:
        print("Missing [identity] section.")
        sys.exit(1)

    servers = []

    for section in config.sections():
        if section.startswith("server."):
            servers.append({
                "name": config[section]["name"],
                "destination_hash": config[section]["destination_hash"]
            })

    if not servers:
        print("No servers configured.")
        sys.exit(1)

    return config["identity"]["file"], servers


def choose_server(servers):
    print()
    print("Available servers")
    print("-----------------")

    for index, server in enumerate(servers, start=1):
        print(f"{index}) {server['name']}")

    while True:
        try:
            choice = int(input("\nSelect server: "))

            if 1 <= choice <= len(servers):
                return servers[choice - 1]

        except ValueError:
            pass

        print("Invalid selection.")


def sql_prompt():
    while True:
        try:
            query = input("rSQL> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not query:
            continue

        if query in (".quit", ".exit"):
            break

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
    RNS.loglevel = RNS.LOG_VERBOSE if args.debug else RNS.LOG_CRITICAL

    identity_file, servers = load_config(args.config)

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
        sql_prompt()
    finally:
        transport.close()


if __name__ == "__main__":
    main()