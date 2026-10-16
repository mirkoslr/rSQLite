"""
Initialize a fresh, default rSQLite user environment.

Responsibilities:
    - Create the rSQLite configuration, identities and GUI directories.
    - Generate the default client and server identities.
    - Compute the server destination hash for client configuration.
    - Write the default client and server configuration files.
    - Initialize the access control list with the client identity hash.
    - Create the local SQLite database.
    - Install the GUI files.
    - Prevent overwriting existing files and roll back newly created files
      if initialization fails.

The environment is created under ~/.rsqlite by default. An alternative home
directory can be provided for testing. Initialization fails if any target
file already exists.

Returns:
    Path: The root directory of the initialized rSQLite environment.

Raises:
    FileExistsError: If any target file already exists.
    Exception: If initialization fails during environment creation.
"""

import configparser
import shutil
import sqlite3
import sysconfig

from pathlib import Path

import RNS

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
    GUI_DIR_NAME,
    GUI_SCRIPT_NAME,
    GUI_MODULE_FILES,
)

def _write_client_config(path, identity_path, destination_hash):
    """Write the client configuration with its identity and
    server destination."""
    config = configparser.ConfigParser()
    config["identity"] = {"file": str(identity_path)}
    config["server.local"] = {
        "name": "local db",
        "destination_hash": destination_hash,
    }
    with path.open("w", encoding="utf-8") as stream:
        config.write(stream)


def _write_server_config(path, identity_path, database_path, allowed_path):
    """Write the server configuration with its identity,
    database and ACL paths."""
    config = configparser.ConfigParser()
    config["server"] = {
        "identity": str(identity_path),
        "database": str(database_path),
        "allowed_identities": str(allowed_path),
    }

    with path.open("w", encoding="utf-8") as stream:
        config.write(stream)


def _get_gui_source_dir():
    """Return the installed directory containing the packaged GUI files."""
    source_dir = Path(sysconfig.get_path("data")) / "share" / "rsqlite" / "gui"
    expected_files = (GUI_SCRIPT_NAME, *GUI_MODULE_FILES)
    missing = [name for name in expected_files if not (source_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(
            f"GUI files not found in {source_dir}: {', '.join(missing)}"
        )
    return source_dir


def _install_gui(gui_dir):
    """Install GUI files without overwriting files already present."""
    gui_names = (GUI_SCRIPT_NAME, *GUI_MODULE_FILES)
    gui_path = gui_dir / GUI_SCRIPT_NAME
    created_gui_files = []

    try:
        source_dir = _get_gui_source_dir()
        existing = [gui_dir / name for name in gui_names if (gui_dir / name).exists()]
        if existing:
            details = ", ".join(str(path) for path in existing)
            raise FileExistsError(f"GUI files already exist and will not be overwritten: {details}")

        gui_dir.mkdir(parents=True, exist_ok=True)
        for name in gui_names:
            destination = gui_dir / name
            shutil.copy2(source_dir / name, destination)
            created_gui_files.append(destination)

        gui_path.chmod(gui_path.stat().st_mode | 0o111)
        return gui_path, None

    except Exception as exc:
        # Remove only GUI files created by this attempt.
        for path in reversed(created_gui_files):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
        return None, exc


def initialize_environment(home=None):
    """Create the default rSQLite environment
    under the user's home directory."""
    root = Path(home).expanduser() if home is not None else Path.home()
    root = root / ".rsqlite"

    config_dir = root / CONFIG_DIR_NAME
    identities_dir = root / IDENTITIES_DIR_NAME
    gui_dir = root / GUI_DIR_NAME

    gui_path = gui_dir / GUI_SCRIPT_NAME

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
        gui_dir.mkdir(parents=True, exist_ok=True)
        print("OK")

        print("[2/6] Creating client identity...", end=" ", flush=True)
        client_identity = prepare_identity(client_identity_path)
        created_files.append(client_identity_path)
        print("OK")

        print("[3/6] Creating server identity...", end=" ", flush=True)
        prepare_identity(server_identity_path)
        created_files.append(server_identity_path)
        print("OK")

        server_identity = RNS.Identity.from_file(str(server_identity_path))
        destination_hash = RNS.Destination.hash_from_name_and_identity(
            f"{APP_NAME}.{SERVICE_NAME}",
            server_identity,
        ).hex()

        print(
            "[4/6] Writing client and server configuration...",
            end=" ",
            flush=True,
        )
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

        print(
            "[6/6] Creating local SQLite database...",
            end=" ",
            flush=True,
        )
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
    print()

    # GUI installation is deliberately separate from core initialization:
    # a GUI packaging/copy error must not undo the usable rSQLite environment.
    print("[GUI] Installing GUI files...", end=" ", flush=True)
    gui_path, gui_error = _install_gui(gui_dir)
    if gui_error is None:
        print("OK")
        print(f"GUI           : {gui_path}")
        print("To use the GUI with NomadNet, create a symbolic link")
        print("in your NomadNet pages directory pointing to this file.")
        print("See INSTALL.md for instructions.")
    else:
        print("FAILED")
        print(f"Reason: {gui_error}")
        print("The rSQLite core initialization completed successfully, but the GUI was not installed.")
        print("To install it manually, read INSTALL.md, download these five files from GitHub,")
        print(f"and copy them into {gui_dir}:")
        for name in (GUI_SCRIPT_NAME, *GUI_MODULE_FILES):
            print(f"  - {name}")
        print("Then create the NomadNet symbolic link as described in INSTALL.md.")

    return root
   