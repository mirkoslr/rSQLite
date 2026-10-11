"""
rSQLite transport layer.

Responsibilities:
- Initialise Reticulum
- Load or create the application Identity
- Discover the remote destination
- Open and close a Link
- Execute SQL requests through the Request/Response API
"""
import RNS
import time
import threading

from .identity import prepare_identity
from .constants import (
    APP_NAME,
    SERVICE_NAME,
    REQUEST_NAME,
    PATH_TIMEOUT,
)

_debug = False

_reticulum = None
_identity = None
_link = None

_link_ready = threading.Event()
_reply_ready = threading.Event()

_response = None
_error = None

def set_debug(enabled):
    """Enable or disable verbose Reticulum logging."""
    global _debug
    _debug = enabled

    if enabled:
        RNS.loglevel = RNS.LOG_VERBOSE
    else:
        RNS.loglevel = RNS.LOG_CRITICAL


def _link_established(link):
    """Handle a successfully established Reticulum Link."""
    global _link

    RNS.log("Link established")

    _link = link
    _link.identify(_identity)
    _link_ready.set()


def _link_closed(link):
    """Handle the closure of a Reticulum Link."""
    global _link

    RNS.log("Link closed")

    _link = None
    _link_ready.clear()


def _response_callback(receipt):
    """Store the response and signal that it is ready."""
    global _response

    _response = receipt.response
    _reply_ready.set()


def _failed_callback(receipt):
    """Store the error and signal that the request has failed."""
    global _error

    _error = "Remote request failed"
    _reply_ready.set()


def connect(identity_file, destination_hash):
    """Connect to a remote rSQLite service."""
    global _reticulum
    global _identity

    _link_ready.clear()

    if _reticulum is None:
        _reticulum = RNS.Reticulum()
        set_debug(_debug)

    _identity = prepare_identity(identity_file)

    destination_hash = bytes.fromhex(destination_hash)

    if not RNS.Transport.has_path(destination_hash):
        RNS.log("Requesting path...")

        RNS.Transport.request_path(destination_hash)

        deadline = time.monotonic() + PATH_TIMEOUT

        while not RNS.Transport.has_path(destination_hash):
            remaining = deadline - time.monotonic()

            if remaining <= 0:
                raise TimeoutError(
                    "Timed out waiting for Reticulum path "
                    f"after {PATH_TIMEOUT} seconds"
                )

            time.sleep(min(0.25, remaining))

    RNS.log("Path available")

    remote_identity = RNS.Identity.recall(destination_hash)

    if remote_identity is None:
        raise RuntimeError("Unable to recall remote identity")

    destination = RNS.Destination(
        remote_identity,
        RNS.Destination.OUT,
        RNS.Destination.SINGLE,
        APP_NAME,
        SERVICE_NAME,
    )

    link = RNS.Link(destination)

    link.set_link_established_callback(_link_established)
    link.set_link_closed_callback(_link_closed)

    if not _link_ready.wait(timeout=15):
        raise TimeoutError("Unable to establish Reticulum Link")


def execute(query: str) -> str:
    """Execute a SQL statement on the remote server."""
    global _response
    global _error

    if _link is None:
        raise RuntimeError("No active Reticulum Link")

    _response = None
    _error = None

    _reply_ready.clear()

    RNS.log("Sending SQL request")

    _link.request(
        REQUEST_NAME,
        query.encode("utf-8"),
        response_callback=_response_callback,
        failed_callback=_failed_callback,
    )

    if not _reply_ready.wait(timeout=30):
        raise TimeoutError("Timed out waiting for server response")

    if _error is not None:
        raise RuntimeError(_error)

    if isinstance(_response, bytes):
        return _response.decode("utf-8")

    return _response


def close():
    """Close the current Link."""
    global _link

    if _link is not None:
        _link.teardown()
        _link = None
    _link_ready.clear()
