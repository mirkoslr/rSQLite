import configparser
import pathlib
import sys


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


def load_server_config(filename):
    config = configparser.ConfigParser()

    if not pathlib.Path(filename).exists():
        print(f"Configuration file '{filename}' not found.")
        sys.exit(1)

    config.read(filename)

    if "server" not in config:
        print("Missing [server] section.")
        sys.exit(1)

    if "announce" not in config:
        print("Missing [announce] section.")
        sys.exit(1)

    server = config["server"]
    announce = config["announce"]

    return {
        "identity": server["identity"],
        "database": server["database"],
        "allowed_identities": server["allowed_identities"],
        "announce_enabled": announce.getboolean("enabled"),
        "announce_at_start": announce.getboolean("announce_at_start"),
    }


