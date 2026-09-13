# rSQLite

**SQLite over Reticulum.**

rSQLite is a lightweight client/server application that provides access to a SQLite database over the [Reticulum Network Stack](https://reticulum.network/).

It combines the simplicity of SQLite with Reticulum's Identity, Destination, Link, and Request/Response mechanisms to provide a small database service.

> **Project status:** rSQLite is currently under active development. The current release is `0.1.0`.

---

## Why rSQLite?

SQLite is deliberately simple: a database can be a single file.

Reticulum provides a resilient application networking layer based on identities, destinations, links, and authenticated communication.

rSQLite combines these two technologies to provide SQLite database access through Reticulum.

---

## Features

- SQLite database access over Reticulum
- Reticulum Identity-based authentication
- Identity allow-list
- Reticulum Link communication
- Request/Response SQL execution
- Command-line client
- Dedicated server process
- Multiple configured remote servers
- systemd integration
- Lightweight Python implementation
- Debian installation script
- Manual installation procedure

---

## Installation

### Debian

The repository includes an automated Debian installer:

```bash
sudo ./install.debian.sh
```

The installer creates the required Python environment, configuration, server identity, access-control file, and systemd service.

> **First-time setup:** A reboot is recommended after installation before using rSQLite for the first time.

### Manual installation

For a manual installation, see:

**[INSTALL.md](INSTALL.md)**

The manual procedure describes the filesystem layout, identities, configuration, access control, systemd service, and client setup.

---

## Quick Start

After installation, start the client:

```bash
rsqlite
```

Select a configured server and enter SQL at the `rSQL>` prompt.

For example:

```sql
SELECT sqlite_version();
```

The SQLite database is created automatically when the server receives its first SQL request.

---

## Download

The source code is available from the GitHub repository.

### Clone with Git

```bash
git clone https://github.com/mirkoslr/rSQLite.git
cd rSQLite
```

### Download ZIP

Download the current source tree from the `main` branch without installing Git:

**[Download rSQLite as ZIP](https://github.com/mirkoslr/rSQLite/archive/refs/heads/main.zip)**

For stable, versioned downloads, see the GitHub **Releases** section when releases are published.

---

## Configuration

The client and server use separate configuration files.

### Client

```text
~/.config/rsqlite/rsqlite-cli.conf
```

A client can contain one or more configured rSQLite servers:

```ini
[identity]

file = /home/USER/.reticulum/identities/rsqlite

[server.local]

name = SERVER_NAME
destination_hash = SERVER_DESTINATION_HASH
```

### Server

```text
/etc/rsqlite/rsqlite-server.conf
```

The server configuration defines:

- Reticulum Identity
- SQLite database
- authorized Identity Hash list
- announce settings

Example:

```ini
[server]

identity = /var/lib/rsqlite/.reticulum/identities/rsqlite-server
database = /var/lib/rsqlite/rsqlite.db
allowed_identities = /etc/rsqlite/allowed_identities

[announce]

enabled = no
announce_at_start = yes
```

rSQLite does not currently implement Reticulum Announce.

The `[announce]` section is reserved for future releases. The current `0.1.0` release does not use these settings.

---

## Authentication and Access Control

rSQLite uses Reticulum Identity authentication together with an explicit server allow-list.

The server maintains an allow-list containing the Identity Hashes of authorized clients.

The allow-list contains **Identity Hashes**, not Destination Hashes.

---

## Current Status

The current `0.1.0` release includes:

- working CLI client
- working server
- Reticulum transport
- Request/Response SQL execution
- SQLite integration
- Identity-based access control
- Debian installer
- systemd server integration
- manual installation documentation

The complete client, Reticulum, server, and SQLite request/response path has been tested on Debian.

---

## License

rSQLite is licensed under the [MIT License](LICENSE).

The rSQLite project itself is distributed under the MIT License. Dependencies, including Reticulum, remain subject to their respective licenses.

---

## Contributing

rSQLite is an experimental open-source project.

Issues, ideas, testing, documentation improvements, and code contributions are welcome.
