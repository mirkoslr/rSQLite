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

import RNS

from identity import prepare_identity
from constants import APP_NAME, SERVICE_NAME, REQUEST_NAME

_database_file=None

def execute_sql(sql):
    try:
        with sqlite3.connect(_database_file) as db:
            cur=db.cursor()
            start = time.perf_counter()
            cur.execute(sql)

            if cur.description is None:
                db.commit()
                elapsed = time.perf_counter() - start
                
                return {"ok":True,
                        "rows_affected":cur.rowcount,
                        "execution_time": elapsed
                        }

            rows = cur.fetchall()
            elapsed = time.perf_counter() - start

            return {
                "ok":True,
                "columns":[c[0] for c in cur.description],
                "rows":rows,
                "execution_time": elapsed
            }
        
    except Exception as e:
        return {"ok":False,"error":str(e)}

def sql_handler(path,data,request_id,link_id,remote_identity,requested_at):
    query=data.decode("utf-8")
    RNS.log(f"SQL request: {query}")
    return json.dumps(execute_sql(query)).encode("utf-8")

def remote_identified(link,identity):
    RNS.log(f"Authenticated peer {RNS.prettyhexrep(identity.hash)}")

def client_connected(link):
    RNS.log("Incoming link established")
    link.set_remote_identified_callback(remote_identified)

def start(identity_file,database_file):
    global _database_file

    RNS.Reticulum()
    identity=prepare_identity(identity_file)
    _database_file=database_file

    destination=RNS.Destination(
        identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
        SERVICE_NAME
    )

    destination.set_link_established_callback(client_connected)
    destination.register_request_handler(
        REQUEST_NAME,
        response_generator=sql_handler,
        allow=RNS.Destination.ALLOW_ALL
    )

    print("rSQLite server ready")
    print("Destination hash:",RNS.prettyhexrep(destination.hash))
    print("Database:",_database_file)

    while True:
        time.sleep(1)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("-i","--identity",default="~/.reticulum/identities/rsqlite-server")
    p.add_argument("-d","--database",required=True)
    a=p.parse_args()
    start(a.identity,a.database)
