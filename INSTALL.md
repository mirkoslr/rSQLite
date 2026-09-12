# rSQLite

## Manual Installation

This document describes how to install rSQLite manually on a Linux system.

The procedure uses the standard Linux filesystem layout and `systemd`.

The commands shown use `sudo` and can be adapted to the package manager of your distribution.

rSQLite can run as a client, a server, or both.

---

## 1. Requirements

The following are required:

- Linux
- Python 3.9 or newer
- Python virtual environment support
- Reticulum (RNS)
- systemd (server only)

rSQLite requires:

```text
rns >= 1.3.9
```

Reticulum must be installed and running independently.

---

## 2. Suggested Paths

The following paths are recommended.

### Server

```text
/opt/rsqlite
/opt/rsqlite/venv

/etc/rsqlite/rsqlite-server.conf
/etc/rsqlite/allowed_identities

/var/lib/rsqlite
/var/lib/rsqlite/rsqlite.db
/var/lib/rsqlite/.reticulum/identities/rsqlite-server

/etc/systemd/system/rsqlite-server.service
```

### Client

```text
~/.config/rsqlite/rsqlite-cli.conf
~/.reticulum/identities/rsqlite
```

---

## 3. Install rSQLite

Create the installation directory:

```bash
sudo mkdir -p /opt/rsqlite
```

Create the Python virtual environment:

```bash
sudo python3 -m venv /opt/rsqlite/venv
```

Install rSQLite from the wheel:

```bash
sudo /opt/rsqlite/venv/bin/pip install rsqlite-0.1.0-py3-none-any.whl
```

The package installs:

```text
/opt/rsqlite/venv/bin/rsqlite
/opt/rsqlite/venv/bin/rsqlite-server
```

---

## 4. Create the Server User

The server runs as a dedicated system user.

Create the user:

```bash
sudo useradd \
    --system \
    --home /var/lib/rsqlite \
    --shell /usr/sbin/nologin \
    rsqlite
```

Create the required directories:

```bash
sudo mkdir -p /etc/rsqlite
sudo mkdir -p /var/lib/rsqlite
```

Set ownership:

```bash
sudo chown -R rsqlite:rsqlite /var/lib/rsqlite
```

---

## 5. Create the Server Identity

Create the Reticulum Identity:

```bash
sudo /opt/rsqlite/venv/bin/python -c \
'from rsqlite.identity import prepare_identity; prepare_identity("/var/lib/rsqlite/.reticulum/identities/rsqlite-server")'
```

Set ownership:

```bash
sudo chown -R rsqlite:rsqlite /var/lib/rsqlite/.reticulum
```

Obtain the Server Identity Hash:

```bash
sudo /opt/rsqlite/venv/bin/python -c \
'import RNS; i=RNS.Identity.from_file("/var/lib/rsqlite/.reticulum/identities/rsqlite-server"); print(i.hash.hex())'
```

The returned value is the Server Identity Hash.

Use the raw hexadecimal value in configuration files.

Do not use `RNS.prettyhexrep()` for configuration values.

---

## 6. Calculate the Server Destination Hash

The rSQLite service is:

```text
rsqlite.database
```

The Destination Hash is derived from the server Identity.

Obtain it with:

```bash
sudo /opt/rsqlite/venv/bin/python -c \
'import RNS; from rsqlite.constants import APP_NAME, SERVICE_NAME; i=RNS.Identity.from_file("/var/lib/rsqlite/.reticulum/identities/rsqlite-server"); h=RNS.Destination.hash_from_name_and_identity(f"{APP_NAME}.{SERVICE_NAME}", i); print(h.hex())'
```

The returned value is the Server Destination Hash.

The two hashes have different meanings:

```text
Identity Hash      identifies the Reticulum Identity
Destination Hash   identifies the rSQLite service
```

---

## 7. Configure the Server

Create:

```text
/etc/rsqlite/rsqlite-server.conf
```

Use:

```ini
[server]

identity = /var/lib/rsqlite/.reticulum/identities/rsqlite-server
database = /var/lib/rsqlite/rsqlite.db
allowed_identities = /etc/rsqlite/allowed_identities

[announce]

enabled = no
announce_at_start = yes
```

---

## 8. Configure Access Control

Create:

```text
/etc/rsqlite/allowed_identities
```

Add one client Identity Hash per line.

Example:

```text
5e175f142801211840af1ab1a388709e
```

Comments and empty lines are ignored.

The value must be the **client Identity Hash**, not the Destination Hash.

---

## 9. Create the Client Identity

Create the Identity directory:

```bash
mkdir -p ~/.reticulum/identities
```

Create the client Identity:

```bash
/opt/rsqlite/venv/bin/python -c \
'from rsqlite.identity import prepare_identity; prepare_identity("~/.reticulum/identities/rsqlite")'
```

Obtain the Client Identity Hash:

```bash
/opt/rsqlite/venv/bin/python -c \
'import RNS; i=RNS.Identity.from_file("~/.reticulum/identities/rsqlite"); print(i.hash.hex())'
```

Add this hash to:

```text
/etc/rsqlite/allowed_identities
```

---

## 10. Configure the Client

Create:

```text
~/.config/rsqlite/rsqlite-cli.conf
```

Example:

```ini
[identity]

file = /home/USER/.reticulum/identities/rsqlite

[server.local]

name = SERVER_NAME
destination_hash = SERVER_DESTINATION_HASH
```

Replace `USER`, `SERVER_NAME`, and `SERVER_DESTINATION_HASH` with the appropriate values.

---

## 11. Create the systemd Service

Create:

```text
/etc/systemd/system/rsqlite-server.service
```

Use:

```ini
[Unit]
Description=rSQLite Server
After=rnsd.service
Requires=rnsd.service

[Service]
Type=simple
User=rsqlite
ExecStart=/opt/rsqlite/venv/bin/python -m rsqlite.server -c /etc/rsqlite/rsqlite-server.conf
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

The service requires `rnsd.service` and starts after it.

---

## 12. Start the Server

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable the service:

```bash
sudo systemctl enable rsqlite-server.service
```

Start the service:

```bash
sudo systemctl start rsqlite-server.service
```

Check the status:

```bash
sudo systemctl status rsqlite-server.service
```

View the logs:

```bash
sudo journalctl -u rsqlite-server.service
```

---

## 13. Test the Client

Make sure Reticulum is running.

Start rSQLite:

```bash
/opt/rsqlite/venv/bin/rsqlite
```

Select the configured server.

The SQL prompt should appear:

```text
rSQL>
```

---

## 14. Test SQL

Check the SQLite version:

```sql
SELECT sqlite_version();
```

Create a test table:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT
);
```

Insert a row:

```sql
INSERT INTO users (name) VALUES ('Test');
```

Read the table:

```sql
SELECT * FROM users;
```

The SQLite database is created automatically when the server receives its first SQL request.

---

## 15. Installation Paths

| Component | Path |
|---|---|
| Software | `/opt/rsqlite` |
| Python environment | `/opt/rsqlite/venv` |
| Server configuration | `/etc/rsqlite/rsqlite-server.conf` |
| Access control | `/etc/rsqlite/allowed_identities` |
| Server data | `/var/lib/rsqlite` |
| Database | `/var/lib/rsqlite/rsqlite.db` |
| Server Identity | `/var/lib/rsqlite/.reticulum/identities/rsqlite-server` |
| systemd service | `/etc/systemd/system/rsqlite-server.service` |
| Client configuration | `~/.config/rsqlite/rsqlite-cli.conf` |
| Client Identity | `~/.reticulum/identities/rsqlite` |

---

## 16. Debian Installer

The repository also provides an automated installer for Debian-based systems:

```text
install.debian.sh
```

The installer automates the procedure described in this document.

To run it:

```bash
sudo ./install.debian.sh
```

### Reboot after installation

After completing the installation, a system reboot is recommended before
using rSQLite for the first time.

The installer configures Reticulum and rSQLite as system services.
Rebooting ensures that the new service environment is fully initialized
before the first client/server test.

After reboot:

```bash
rsqlite
```

For other Linux distributions, install the required system packages using the distribution's package manager and follow this manual procedure.
