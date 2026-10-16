**# Installation**

**## Requirements**

You need:

\- Python 3.9 or newer
\- `pipx`

Reticulum is installed automatically as a dependency of rSQLite.

**## Get rSQLite**

You can get rSQLite in two ways.

**### Option 1 — Clone with Git**

```bash
git clone [https://github.com/mirkoslr/rSQLite.git](https://github.com/mirkoslr/rSQLite.git)
cd rSQLite
```

**### Option 2 — Download the ZIP**

Open the rSQLite repository on GitHub, choose **\*\*Code → Download ZIP\*\***, and extract the archive.

Then open a terminal in the extracted `rSQLite` directory.

**## Install rSQLite**

On Linux, macOS, or Windows, open a terminal in the extracted `rSQLite` directory and run:

```bash
pipx install .
```

Verify the installation:

```bash
rsqlite --help
```

If the command is available, rSQLite is installed correctly.

**## Start the server**

Start the server with:

```bash
rsqlite-server
```

The server uses:

```text
~/.rsqlite/config/rsqlite-server.conf
```

as its default configuration file.

Server data is stored under:

```text
~/.rsqlite/
```

**## Start the client**

Run:

```bash
rsqlite
```

The client uses:

```text
~/.rsqlite/config/rsqlite-cli.conf
```

for its configuration.

**## Initialize rSQLite**

Before using rSQLite, initialize its environment:

```bash
rsqlite --init
```

Initialization creates the default rSQLite environment, including the configuration files, identities, access-control settings, database, and GUI files under `~/.rsqlite/`.

The GUI files are installed automatically when they are available in the installed package. If GUI installation fails, the core rSQLite initialization can still complete successfully; see **\*\*Manual GUI installation\*\*** below.

**## GUI installation**

rSQLite includes a GUI designed to run as a local page in NomadNet.

**### Automatic installation**

During `rsqlite --init`, rSQLite attempts to copy the GUI files into:

```text
~/.rsqlite/gui/
```

The GUI consists of five files:

\- `rsqlite-gui.py`
\- `database.py`
\- `handlers.py`
\- `links.py`
\- `views.py`

If the files are available in the installed package, they are copied automatically. The main GUI script is also made executable.

After the GUI files have been installed, create a symbolic link named `rsqlite-gui.py` in your NomadNet pages directory. See **\*\*Create the NomadNet symbolic link\*\*** below for instructions.

If GUI installation fails, the core rSQLite initialization can still complete successfully. In that case, follow the **\*\*Manual GUI installation\*\*** instructions below.

**### Create the NomadNet symbolic link**

After installing the GUI files, create a symbolic link named `rsqlite-gui.py` in your NomadNet pages directory.

The link must point to:

```text
~/.rsqlite/gui/rsqlite-gui.py
```

For example, if your NomadNet pages directory is `~/.nomadnetwork/storage/pages/`, run:

```bash
ln -s "$HOME/.rsqlite/gui/rsqlite-gui.py" \
     "$HOME/.nomadnetwork/storage/pages/rsqlite-gui.py"
```

**\*\*Note:\*\*** The path above is an example. If your NomadNet pages directory is different, replace it with the correct path for your installation.

Open NomadNet and navigate to the `rsqlite-gui.py` page to launch the GUI.

**### Manual GUI installation**

If rSQLite reports that the GUI files could not be installed automatically, download the five files from the repository:

\- [`rsqlite-gui.py`]([https://github.com/mirkoslr/rSQLite/blob/main/gui/rsqlite-gui.py](https://github.com/mirkoslr/rSQLite/blob/main/gui/rsqlite-gui.py))
\- [`database.py`]([https://github.com/mirkoslr/rSQLite/blob/main/gui/database.py](https://github.com/mirkoslr/rSQLite/blob/main/gui/database.py))
\- [`handlers.py`]([https://github.com/mirkoslr/rSQLite/blob/main/gui/handlers.py](https://github.com/mirkoslr/rSQLite/blob/main/gui/handlers.py))
\- [`links.py`]([https://github.com/mirkoslr/rSQLite/blob/main/gui/links.py](https://github.com/mirkoslr/rSQLite/blob/main/gui/links.py))
\- [`views.py`]([https://github.com/mirkoslr/rSQLite/blob/main/gui/views.py](https://github.com/mirkoslr/rSQLite/blob/main/gui/views.py))

Create the destination directory if it does not exist:

```bash
mkdir -p "$HOME/.rsqlite/gui"
```

Copy all five files into:

```text
~/.rsqlite/gui/
```

Make the main GUI script executable:

```bash
chmod +x "$HOME/.rsqlite/gui/rsqlite-gui.py"
```

Then create the NomadNet symbolic link using the instructions above.

**## Troubleshooting**

**### GUI fails to start: `ModuleNotFoundError: No module named 'rsqlite'`**

Depending on how NomadNet and rSQLite are installed, they may use separate Python virtual environments. In this case, the Python interpreter used by NomadNet cannot find the `rsqlite` module because it is installed in a different environment.

**Workarounds**

**Option 1 — Use the rSQLite Python interpreter (recommended)**

Edit the first line (shebang) of `~/.rsqlite/gui/rsqlite-gui.py` to point to the Python interpreter in the rSQLite virtual environment, instead of using `#!/usr/bin/env python3`, which may select NomadNet's interpreter.

To find the correct path, run:

```bash
pipx environment
```

Look for the variable `PIPX_LOCAL_VENVS`. It indicates the directory where pipx stores the separate Python virtual environments for installed applications. Each application has its own environment and Python interpreter.

Inside this directory, locate `rsqlite/bin/python`. Use its full path to replace the first line (shebang) in `~/.rsqlite/gui/rsqlite-gui.py`.

For example, on Linux:

```python
#!/home/<username>/.local/share/pipx/venvs/rsqlite/bin/python
```

On macOS:

```python
#!/Users/<username>/Library/Application Support/pipx/venvs/rsqlite/bin/python
```

Replace `<username>` with your system username and adjust the path if your pipx virtual environments are stored elsewhere.

**Option 2 — Inject rSQLite into NomadNet's environment**

Alternatively, install rSQLite in NomadNet's virtual environment:

```bash
pipx inject nomadnet rsqlite
```

See the [pipx injection documentation](https://pipx.pypa.io/latest/how-to/inject-packages.html).

**We recommend Option 1** to keep the NomadNet and rSQLite environments separate. A future version of rSQLite is planned to provide a launcher that selects the correct Python interpreter automatically.

**## Verify the installation**

Verify the server command:

```bash
rsqlite-server --help
```

The two commands provided by rSQLite are:

```text
rsqlite
rsqlite-server
```

Reticulum is installed automatically as a dependency. `rnsd` is not required to run rSQLite.
