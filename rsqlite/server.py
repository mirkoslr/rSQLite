#!/usr/bin/env python3
"""
rSQLite server.

Uses one SQLite connection per request so it is thread-safe with
Reticulum Request/Response worker threads.
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
    query = data.decode("utf-8")
    RNS.log(f"SQL request: {query}")

    return json.dumps(
        execute_sql(query)
    ).encode("utf-8")


def remote_identified(link, identity):
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
    RNS.log("Incoming link established")
    link.set_remote_identified_callback(remote_identified)


def start(server_config, rns_configdir=None):
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
    p = argparse.ArgumentParser()

    p.add_argument(
        "-c",
        "--config",
        default=Path.home() / ".config" / "rsqlite" / "rsqlite-server.conf",
        help="Server configuration file"
    )

    p.add_argument(
        "--rns-config",
        default=None,
        help="Reticulum configuration directory"
    )

    a = p.parse_args()

    server_config = config.load_server_config(a.config)

    start(
        server_config,
        rns_configdir=a.rns_config
    )


if __name__ == "__main__":
    main()
    