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

* SQLite database access over Reticulum
* Reticulum Identity-based authentication
* Identity allow-list
* Reticulum Link communication
* Request/Response SQL execution
* Command-line client
* Dedicated server process
* Multiple configured remote servers
* Lightweight Python implementation
* Standard Python package installation
* `pipx` installation support
* Optional Reticulum configuration directory

---

## Installation

rSQLite is distributed as a normal Python application.

### Requirements

* Linux
* macOS
* Windows
* Python 3.9 or newer
* `pipx` (recommended)

Reticulum is installed automatically as a Python dependency of rSQLite.

rSQLite runs as a normal Reticulum application and does not require a separate Reticulum daemon.

### Install with pipx

From the repository:

```bash
git clone https://github.com/mirkoslr/rSQLite.git
cd rSQLite
pipx install .
```

The installation provides:

```text
rsqlite
rsqlite-server
```

### Automated installation

For Linux systems, the repository also includes an automated installer:

```bash
./install.sh
```

The installer prepares the rSQLite package, configuration, server Identity, access-control file, and database layout for the current user.

The automated installer is intended for Linux systems. On macOS and Windows, rSQLite can be installed directly as a Python application using `pipx` or `pip` where appropriate.

For the complete installation procedure, see:

**[INSTALL.md](INSTALL.md)**

---

## Quick Start

### Start the server

The server is a normal application process.

For a Linux installation performed with `install.sh`:

```bash
rsqlite-server -c ~/.config/rsqlite/rsqlite-server.conf
```

The server prints its Reticulum Destination Hash when it starts:

```text
rSQLite server ready
Destination hash: ...
Database: /home/USER/.rsqlite/rsqlite.db
```

The Destination Hash can then be configured in the client configuration.

For manual installations, the server configuration file can be stored anywhere and specified with `-c` / `--config`:

```bash
rsqlite-server -c /path/to/rsqlite-server.conf
```

### Start the client

In another terminal:

```bash
rsqlite
```

Select a configured server and enter SQL at the `rSQL>` prompt.

For example:

```sql
SELECT sqlite_version();
```

The client establishes a Reticulum Link to the configured server and sends the SQL statement through the Reticulum Request/Response mechanism.

---

## Configuration

The client and server use separate configuration files.

### Client

The default client configuration is:

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

The client Identity is used to identify the application when establishing the Reticulum Link.

### Server

When installed with the Linux `install.sh` installer, the default server configuration is:

```text
~/.config/rsqlite/rsqlite-server.conf
```

For manual installations, the server configuration file can be stored anywhere and passed explicitly with `-c` / `--config`.

The server configuration defines:

* Reticulum Identity
* SQLite database
* authorized Identity Hash list
* announce settings

Example:

```ini
[server]

identity = /home/USER/.rsqlite/identities/rsqlite-server

database = /home/USER/.rsqlite/rsqlite.db

allowed_identities = /home/USER/.config/rsqlite/allowed_identities

[announce]

enabled = no

announce_at_start = yes
```

rSQLite does not currently implement Reticulum Announce.

The `[announce]` section is reserved for future releases. The current `0.1.0` release does not use these settings.

---

## Reticulum Configuration

rSQLite uses the Reticulum configuration available to the current execution context.

The server can optionally use a specific Reticulum configuration directory:

```bash
rsqlite-server \
   -c ~/.config/rsqlite/rsqlite-server.conf \
   --rns-config /path/to/reticulum
```

The `-c` / `--config` option specifies the rSQLite configuration file, while `--rns-config` specifies the Reticulum configuration directory.

These are independent configuration settings.

---

## Authentication and Access Control

rSQLite uses Reticulum Identity authentication together with an explicit server allow-list.

The server maintains an allow-list containing the Identity Hashes of authorized clients.

The allow-list contains **Identity Hashes**, not Destination Hashes.

For example:

```text
caf2gle913dd86f44d13e62debft8f50
```

When a client establishes a Link, the client identifies itself using its Reticulum Identity.

The server checks that Identity against the configured allow-list before accepting requests.

---

## Architecture

The basic communication path is:

```text
rSQLite client
     │
     │ RNS.Reticulum()
     ▼
 Reticulum
     │
     │ Link
     ▼
rSQLite server
     │
     │ Request/Response
     ▼
  SQLite
```

Both the client and server are normal Reticulum applications.

If a shared Reticulum instance is available, the application can use Reticulum's shared-instance mechanism according to the active Reticulum configuration.

---

## Deployment

rSQLite does not impose a specific server deployment model.

The server can be started manually:

```bash
rsqlite-server -c /path/to/rsqlite-server.conf
```

or integrated into an operating-system service manager if persistent or automatic execution is required.

Service management is therefore a deployment choice rather than part of the rSQLite installation.

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

## Current Status

The current `0.1.0` release includes:

* working CLI client
* working server
* Reticulum transport
* Request/Response SQL execution
* SQLite integration
* Identity-based access control
* multiple configured servers
* pipx installation support
* Linux installation script
* manual installation documentation
* optional Reticulum configuration selection

The complete client, Reticulum, server, and SQLite request/response path has been tested successfully on Linux and macOS.

---

## Contributing

rSQLite is an experimental open-source project.

Issues, ideas, testing, documentation improvements, and code contributions are welcome.
