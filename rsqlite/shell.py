"""
rSQLite SQL shell.

Responsibilities:
- Map shell commands to SQL queries
- Execute SQL commands
- Normalize query responses
"""

import json

from rsqlite import formatter
from rsqlite import transport

def dispatch_command(line):
    """Identify a client command and extract its argument, if any."""
    parts = line.split()

    if not parts:
        return None, None

    if parts[0] in (".quit", ".exit"):
        return "quit", None

    if parts[0] == ".help":
        return "help", None

    if parts[0] == ".tables":
        return "tables", None

    if parts[0] == ".schema":
        arg = parts[1] if len(parts) > 1 else None
        return "schema", arg

    if parts[0] == ".indexes":
        return "indexes", None

    if parts[0] == ".databases":
        return "databases", None

    if parts[0] == ".version":
        return "version", None

    if parts[0] == ".db":
        return "databases_configured", None

    return None, None


def get_command_query(cmd, arg=None):
    """Return the SQL query associated with a client command."""
    if cmd == "tables":
        return """
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
"""

    if cmd == "schema":
        if arg:
            table_name = arg.replace('"', '""')
            return f'PRAGMA table_info("{table_name}");'
        return """
SELECT name, sql
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
"""

    if cmd == "indexes":
        return """
SELECT name
FROM sqlite_master
WHERE type = 'index'
ORDER BY name;
"""

    if cmd == "databases":
        return """
PRAGMA database_list;
"""

    if cmd == "version":
        return """
SELECT sqlite_version();
"""

    return None


def execute_sql(query):
    """Execute a SQL query and decode the server response if needed."""
    response = transport.execute(query)

    if isinstance(response, str):
        return json.loads(response)

    return response


def render_response(response):
    """Format a server response for display."""
    return formatter.render(response)


def execute_command(cmd, arg=None, servers=None):
    """Handle client commands and execute their SQL queries."""
    if cmd == "help":
        return """Commands:
  .help       Show this help
  .tables     List tables
  .schema     Show table schema
  .indexes    List indexes
  .databases  List databases
  .db         List configured servers
  .version    Show rSQL version
  .quit       Exit rSQL
  .exit       Exit rSQL"""

    if cmd == "databases_configured":

        if servers is None:
            return "No server configuration available."

        lines = [
            "",
            "Configured servers",
            "------------------",
        ]

        for index, server in enumerate(servers, start=1):
            lines.append(
                f"{index}) {server['name']}"
            )
            lines.append(
                f"   Destination: {server['destination_hash']}"
            )

        return "\n".join(lines)
    
    query = get_command_query(cmd, arg)

    # Ensure a query exists before execution, especially if commands
    # are later accepted from external sources.
    if query is None:
        return None

    return execute_sql(query)


def execute_and_render(query):
    """Execute a SQL query and format the response for display."""
    response = execute_sql(query)
    return render_response(response)
