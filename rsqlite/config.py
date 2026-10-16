"""
rSQLite configuration module.

Responsibilities:
- Load and validate the client configuration
- Load and validate the server configuration
- Read the application Identity and server settings
- Return configuration data to the client and server
"""

import configparser
import pathlib
import sys

def load_config(filename):
    """Load the client configuration and return the identity file path
    and the list of configured servers.
    """
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
    """Load and validate the server configuration file."""
    config = configparser.ConfigParser()

    if not pathlib.Path(filename).exists():
        print(f"Configuration file '{filename}' not found.")
        sys.exit(1)

    config.read(filename)

    if "server" not in config:
        print("Missing [server] section.")
        sys.exit(1)

    server = config["server"]
    
    return {
        "identity": server["identity"],
        "database": server["database"],
        "allowed_identities": server["allowed_identities"],
    }
