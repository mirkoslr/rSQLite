"""Create a fresh, default rSQLite user environment."""

import configparser
import sqlite3
from pathlib import Path

import RNS

from rsqlite.constants import APP_NAME, SERVICE_NAME
from rsqlite.identity import prepare_identity
from rsqlite.constants import (
    APP_NAME,
    SERVICE_NAME,
    CONFIG_DIR_NAME,
    IDENTITIES_DIR_NAME,
    CLIENT_IDENTITY_NAME,
    SERVER_IDENTITY_NAME,
    CLIENT_CONFIG_NAME,
    SERVER_CONFIG_NAME,
    ALLOWED_IDENTITIES_NAME,
    DATABASE_NAME,
)




def _write_client_config(path, identity_path, destination_hash):
    config = configparser.ConfigParser()
    config["identity"] = {"file": str(identity_path)}
    config["server.local"] = {
        "name": "local db",
        "destination_hash": destination_hash,
    }
    with path.open("w", encoding="utf-8") as stream:
        config.write(stream)


def _write_server_config(path, identity_path, database_path, allowed_path):
    config = configparser.ConfigParser()
    config["server"] = {
        "identity": str(identity_path),
        "database": str(database_path),
        "allowed_identities": str(allowed_path),
    }
   
    with path.open("w", encoding="utf-8") as stream:
        config.write(stream)


def initialize_environment(home=None):
    """Create the default client/server identities, configs, ACL and SQLite DB.

    Existing target files are never overwritten. The function returns the root
    directory on success and raises an exception if initialization fails.
    """
    root = Path(home).expanduser() if home is not None else Path.home()
    root = root / ".rsqlite"
    config_dir = root / CONFIG_DIR_NAME
    identities_dir = root / IDENTITIES_DIR_NAME

    client_identity_path = identities_dir / CLIENT_IDENTITY_NAME
    server_identity_path = identities_dir / SERVER_IDENTITY_NAME
    client_config_path = config_dir / CLIENT_CONFIG_NAME
    server_config_path = config_dir / SERVER_CONFIG_NAME
    allowed_identities_path = config_dir / ALLOWED_IDENTITIES_NAME
    database_path = root / DATABASE_NAME

    targets = (
        client_identity_path,
        server_identity_path,
        client_config_path,
        server_config_path,
        allowed_identities_path,
        database_path,
    )
    existing = [path for path in targets if path.exists()]
    if existing:
        details = "\n".join(f"  - {path}" for path in existing)
        raise FileExistsError(
            "Initialization would overwrite existing rSQLite files. "
            "No files were changed:\n" + details
        )

    created_files = []
    print()
    print("rSQLite initialization")
    print("----------------------")

    try:
        print("[1/6] Creating directory structure...", end=" ", flush=True)
        config_dir.mkdir(parents=True, exist_ok=True)
        identities_dir.mkdir(parents=True, exist_ok=True)
        print("OK")

        print("[2/6] Creating client identity...", end=" ", flush=True)
        client_identity = prepare_identity(client_identity_path)
        created_files.append(client_identity_path)
        print("OK")

        print("[3/6] Creating server identity...", end=" ", flush=True)
        server_identity = prepare_identity(server_identity_path)
        created_files.append(server_identity_path)
        print("OK")

        server_identity = RNS.Identity.from_file(str(server_identity_path))
        destination_hash = RNS.Destination.hash_from_name_and_identity(
            f"{APP_NAME}.{SERVICE_NAME}",
            server_identity,
        ).hex()

        print("[4/6] Writing client and server configuration...", end=" ", flush=True)
        _write_client_config(
            client_config_path,
            client_identity_path,
            destination_hash,
        )
        created_files.append(client_config_path)
        _write_server_config(
            server_config_path,
            server_identity_path,
            database_path,
            allowed_identities_path,
        )
        created_files.append(server_config_path)
        print("OK")

        print("[5/6] Creating allowed identities...", end=" ", flush=True)
        allowed_identities_path.write_text(
            "# rSQLite authorized client Identity Hashes\n"
            "# One Reticulum Identity Hash per line.\n"
            f"{client_identity.hash.hex()}\n",
            encoding="utf-8",
        )
        created_files.append(allowed_identities_path)
        print("OK")

        print("[6/6] Creating local SQLite database...", end=" ", flush=True)
        with sqlite3.connect(database_path):
            created_files.append(database_path)
        print("OK")

    except Exception:
        # Remove files created by this run, so a failed init can be retried.
        for path in reversed(created_files):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
        raise

    print()
    print("Initialization completed successfully.")
    print(f"Configuration : {config_dir}")
    print(f"Identities    : {identities_dir}")
    print(f"Local database: {database_path}")
    print("Start the server with: rsqlite-server")
    print("Start the client with: rsqlite")
    return root

