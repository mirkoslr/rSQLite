# Installation

## Requirements

You need:

- Python 3.9 or newer
- `pipx`

Reticulum is installed automatically as a dependency of rSQLite.

## Get rSQLite

You can get rSQLite in two ways.

### Option 1 — Clone with Git

```bash
git clone https://github.com/mirkoslr/rSQLite.git
cd rSQLite
```

### Option 2 — Download the ZIP

Open the rSQLite repository on GitHub, choose **Code → Download ZIP**, and extract the archive.

Then open a terminal in the extracted `rSQLite` directory.

## Linux

Run the installer:

```bash
./install.sh
```

## macOS

Open a terminal in the extracted `rSQLite` directory and install rSQLite with `pipx`:

```bash
pipx install .
```

Verify the installation:

```bash
rsqlite --help
```

If the command is available, rSQLite is installed correctly.

### Start the server

If you installed the server, start it with:

```bash
rsqlite-server
```

The server uses:

```text
~/.config/rsqlite/rsqlite-server.conf
```

as its default configuration file.

Server data is stored under:

```text
~/.rsqlite/
```

### Start the client

Run:

```bash
rsqlite
```

The client uses:

```text
~/.config/rsqlite/rsqlite-cli.conf
```

for its configuration.

## Windows

Open PowerShell in the extracted `rSQLite` directory and run:

```powershell
pipx install .
```

Verify the installation:

```powershell
rsqlite --help
```

If the command is available, rSQLite is installed correctly.

## Verify the installation

You can also verify the server command:

```bash
rsqlite-server --help
```

The two commands provided by rSQLite are:

```text
rsqlite
rsqlite-server
```

Reticulum is installed automatically as a dependency. `rnsd` is not required to run rSQLite.

For more information about configuration and usage, see the rest of this guide.

