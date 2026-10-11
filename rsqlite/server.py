#!/usr/bin/env python3
"""
rSQLite server.

Responsibilities:
- Handle incoming SQL requests
- Execute queries against SQLite
- Return query results to the client
- Use one SQLite connection per request for thread safety
  with Reticulum Request/Response worker threads
"""
import argparse
import json
import sqlite3
import time
from pathlib import Path

import RNS

from rsqlite import config
from rsqlite.identity import prepare_identity
from rsqlite.constants import APP_NAME, SERVICE_NAME, REQUEST_NAME

_database_file = None
_allowed_identity_hashes = []

def load_allowed_identities(path):
    """Load and validate allowed Reticulum Identity Hashes from a file."""
    allowed = []

    path = Path(path).expanduser()

    with open(path, "r") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue
            try:
                identity_hash = bytes.fromhex(line)
            except ValueError:
                raise ValueError(
                    f"Invalid Identity Hash in {path} at line {line_number}: {line}"
                )
            
            expected_length = RNS.Identity.TRUNCATED_HASHLENGTH // 8

            if len(identity_hash) != expected_length:
                raise ValueError(
                    f"Invalid Identity Hash length in {path} "
                    f"at line {line_number}: {line}"
                )
            
            allowed.append(identity_hash)

    return allowed


def execute_sql(sql):
    """Execute an SQL query and return the result."""
    try:
        with sqlite3.connect(_database_file) as db:
            cur = db.cursor()
            start = time.perf_counter()
            cur.execute(sql)

            if cur.description is None:
                db.commit()
                elapsed = time.perf_counter() - start

                return {
                    "ok": True,
                    "rows_affected": cur.rowcount,
                    "execution_time": elapsed
                }

            rows = cur.fetchall()
            elapsed = time.perf_counter() - start

            return {
                "ok": True,
                "columns": [c[0] for c in cur.description],
                "rows": rows,
                "execution_time": elapsed
            }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }


def sql_handler(
    path,
    data,
    request_id,
    link_id,
    remote_identity,
    requested_at
):
    """Execute an SQL request and return the JSON-encoded 
    result to the client."""
    query = data.decode("utf-8")
    RNS.log(f"SQL request: {query}")

    return json.dumps(
        execute_sql(query)
    ).encode("utf-8")


def remote_identified(link, identity):
    """Authorize the remote identity or close the link if unauthorized."""
    if identity.hash in _allowed_identity_hashes:
        RNS.log(
            f"Authorized peer {RNS.prettyhexrep(identity.hash)}"
        )
        return

    RNS.log(
        f"Unauthorized peer {RNS.prettyhexrep(identity.hash)}"
    )

    link.teardown()


def client_connected(link):
    """Handle a newly established incoming link."""
    RNS.log("Incoming link established")
    link.set_remote_identified_callback(remote_identified)


def print_identity(server_config, rns_configdir=None):
    """Print the server identity and destination information.
   Initialize Reticulum and load the server identity.
    """
    RNS.Reticulum(configdir=rns_configdir)

    identity_file = server_config["identity"]
    identity = prepare_identity(identity_file)

    destination = RNS.Destination(
        identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
        SERVICE_NAME,
    )

    print("rSQLite Server Identity")
    print("-----------------------")
    print(f"Identity file    : {identity_file}")
    print(f"Identity hash    : {RNS.prettyhexrep(identity.hash)}")
    print(f"Destination hash : {RNS.prettyhexrep(destination.hash)}")


def start(server_config, rns_configdir=None):
    """Initialize Reticulum and start the rSQLite server.
    Register the destination and request handler, then keep the server running.
    """
    global _database_file
    global _allowed_identity_hashes

    identity_file = server_config["identity"]

    database_file = Path(
        server_config["database"]
    ).expanduser()

    allowed_identities_file = Path(
        server_config["allowed_identities"]
    ).expanduser()

    RNS.Reticulum(configdir=rns_configdir)

    identity = prepare_identity(identity_file)

    _database_file = str(database_file)

    _allowed_identity_hashes = load_allowed_identities(
        allowed_identities_file
    )

    destination = RNS.Destination(
        identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
        SERVICE_NAME
    )

    destination.set_link_established_callback(
        client_connected
    )

    destination.register_request_handler(
        REQUEST_NAME,
        response_generator=sql_handler,
        allow=RNS.Destination.ALLOW_LIST,
        allowed_list=_allowed_identity_hashes
    )

    print("rSQLite server ready")
    print(
        "Destination hash:",
        RNS.prettyhexrep(destination.hash)
    )
    print("Database:", _database_file)

    while True:
        time.sleep(1)


def main():
    """Parse command-line arguments and start the rSQLite server."""
    p = argparse.ArgumentParser()

    p.add_argument(
        "-c",
        "--config",
        default=Path.home() / ".rsqlite" / "config" / "rsqlite-server.conf",
        help="Server configuration file"
    )

    p.add_argument(
        "--rns-config",
        default=None,
        help="Reticulum configuration directory"
    )

    p.add_argument(
        "--print-identity",
        action="store_true",
        help="Print server identity and destination information, then exit",
    )

    a = p.parse_args()

    server_config = config.load_server_config(a.config)

    if a.print_identity:
        print_identity(
            server_config,
            rns_configdir=a.rns_config,
        )
        return
    
    start(
        server_config,
        rns_configdir=a.rns_config
    )


if __name__ == "__main__":
    main()
    