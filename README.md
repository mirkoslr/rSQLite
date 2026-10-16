# rSQLite

**SQLite over Reticulum.**

rSQLite is a lightweight application that provides access to SQLite databases over the [Reticulum Network Stack](https://reticulum.network/).

It combines SQLite with Reticulum's identity-based authentication and encrypted Link communication to provide remote database access through a command-line client and a graphical interface for NomadNet.

> **Project status:** rSQLite is under active development. Current version: `0.1.0`.

## Features

- SQLite database access over Reticulum
- Interactive command-line client
- Graphical interface through NomadNet
- Support for multiple configured remote servers
- Identity-based client authentication
- Installation with `pipx`

## Installation

### Requirements

- Python 3.9 or newer
- [Reticulum](https://reticulum.network/)
- [NomadNet](https://github.com/markqvist/NomadNet) for the graphical interface

Reticulum is installed automatically as a dependency of rSQLite.

### Install with pipx

You can obtain the source code by cloning the repository:

```bash
git clone https://github.com/mirkoslr/rSQLite.git
cd rSQLite
pipx install .
```

Alternatively, download the [ZIP archive](https://github.com/mirkoslr/rSQLite/archive/refs/heads/main.zip), extract it, open a terminal in the extracted directory, and run:

```bash
pipx install .
```

The installation provides the following commands:

- `rsqlite` — command-line client
- `rsqlite-server` — database server

For complete installation and configuration instructions, see [INSTALL.md](INSTALL.md).

## Quick Start

### 1. Initialize rSQLite

Initialize the default rSQLite environment:

```bash
rsqlite --init
```

Initialization creates the default configuration files, identities, access-control settings, and database. It also attempts to install the NomadNet GUI files automatically. If GUI installation fails, the core initialization can still succeed; see [INSTALL.md](INSTALL.md) for manual GUI installation instructions.

### 2. Start the server

Start the server using its default configuration:

```bash
rsqlite-server
```

The default server configuration file is:

```text
~/.rsqlite/config/rsqlite-server.conf
```

To use a configuration file stored at a different location, specify it with `-c` or `--config`:

```bash
rsqlite-server -c /path/to/rsqlite-server.conf
```

When the server starts, it displays its Reticulum Destination Hash. Configure this hash in the client configuration before connecting.

### 3. Verify the client and server identities

To display the Reticulum Identity information used by the client, run:

```bash
rsqlite --print-identity
```

To display the server Identity information and Destination Hash, run:

```bash
rsqlite-server --print-identity
```

The Identity Hash is used when configuring the server's access-control list. The Destination Hash is used by the client to connect to the server.

See [INSTALL.md](INSTALL.md) for installation and initialization details. More usage notes can be added here as the project develops.

### 4. Connect to the server

Start the command-line client:

```bash
rsqlite
```

Select a configured server and enter SQL at the `rSQL>` prompt. Enter `.help` at the prompt to display the available help information.

For example:

```sql
SELECT sqlite_version();
```

The client establishes a Reticulum Link to the selected server and executes SQL statements through the Request/Response mechanism.

### Export a table from the command line

The CLI can export a database table in CSV, JSON, or plain-text format:

```text
-e, --export TABLE       Export a database table
-f, --format {csv,json,txt}
-o, --output FILE        Output file path
```

For example, the export options let you select the table, choose the output format, and optionally specify the output file path.

### Graphical interface

rSQLite also provides a graphical interface through NomadNet. The GUI allows users to browse database tables and view records, insert and delete records, and use an integrated SQL shell through NomadNet's page-based interface.

The GUI uses the same underlying client/server communication model as the command-line client. For GUI installation and instructions on creating the NomadNet page symlink, see [INSTALL.md](INSTALL.md).

NomadNet runs dynamic page scripts separately, so the GUI establishes a Reticulum Link when a page script starts, reuses it for requests handled during that execution, and closes it when the script finishes. Navigating to another page may therefore require a new Link. According to the [official Reticulum manual](https://reticulum.network/manual/understanding.html), establishing a Link involves three packets totalling approximately **297 bytes**, while keeping it open consumes about **0.45 bits per second**. Additional network traffic depends on the SQL requests, the size of their responses, and Reticulum's protocol overhead.

## Troubleshooting

If the GUI fails to start with `ModuleNotFoundError: No module named 'rsqlite'`, NomadNet and rSQLite may be using separate Python environments.

See [INSTALL.md](INSTALL.md#troubleshooting) for the explanation and workarounds.

## Configuration

rSQLite uses separate configuration files for the client and server.

### Client configuration

The default client configuration file is:

```text
~/.rsqlite/config/rsqlite-cli.conf
```

Example:

```ini
[identity]
file = /home/USER/.reticulum/identities/rsqlite

[server.local]
name = SERVER_NAME
destination_hash = SERVER_DESTINATION_HASH
```

The client Identity identifies the application when establishing a Reticulum Link.

Multiple servers can be configured using separate server sections.

### Server configuration

The default server configuration file is:

```text
~/.rsqlite/config/rsqlite-server.conf
```

The configuration file can be stored elsewhere and specified using `-c` or `--config`.

Example:

```ini
[server]
identity = /home/USER/.rsqlite/identities/rsqlite-server
database = /home/USER/.rsqlite/rsqlite.db
allowed_identities = /home/USER/.rsqlite/config/allowed_identities
```

The server configuration defines:

- The server Identity
- The SQLite database file
- The file containing authorized client Identity Hashes

See [INSTALL.md](INSTALL.md) for installation and configuration details.

## Reticulum Configuration

rSQLite uses the Reticulum configuration available to the current execution context.

The server can optionally use a specific Reticulum configuration directory:

```bash
rsqlite-server \
  -c ~/.rsqlite/config/rsqlite-server.conf \
  --rns-config /path/to/reticulum
```

The `-c` / `--config` option specifies the rSQLite configuration file, while `--rns-config` specifies the Reticulum configuration directory.

These are independent settings.

## Authentication and Access Control

rSQLite uses Reticulum Identity authentication and a server-side allow-list to control client access.

The allow-list contains the **Identity Hashes of authorized clients**, not Destination Hashes.

When a client establishes a Link, the server checks the client's Identity against the configured allow-list before accepting requests.

Only authorized client identities are permitted to access the database through rSQLite.

## Database Operations

The command-line client accepts SQL statements at the `rSQL>` prompt. The NomadNet GUI provides a page-based interface for browsing tables and viewing records. The SQL operations available depend on the server implementation and the database; use SQL statements supported by SQLite.

## Deployment

The server can be started manually or managed by an operating-system service manager for persistent or automatic execution.

For example:

```bash
rsqlite-server
```

Service management is a deployment choice and is not required by rSQLite itself.

## Releases

For versioned releases, see the project's [GitHub Releases](https://github.com/mirkoslr/rSQLite/releases) page.

## Current Status

The current `0.1.0` release includes:

- Command-line client
- NomadNet graphical interface
- Database server
- Reticulum transport
- Request/Response SQL execution
- SQLite integration
- Identity-based access control
- Multiple configured servers
- Python package installation support
- Manual installation and configuration support

The client, Reticulum transport, server, and SQLite request/response path have been tested successfully on Linux and macOS.

rSQLite is still under active development, and features and documentation may change between releases.

## Contributing

rSQLite is an experimental open-source project.

Issues, testing, suggestions, documentation improvements, and code contributions are welcome.
