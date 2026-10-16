"""
rSQLite result formatter.

Responsibilities:
- Format SQL query results as readable terminal tables
- Display query status and execution information
"""
import json

def format_value(value, width=None):
    """Convert a value to text and optionally align it 
    to a given width."""
    if value is None:
        text = "NULL"
    else:
        text = str(value)

    if width is None:
        return text

    if isinstance(value, (int, float)):
        return text.rjust(width)

    return text.ljust(width)


def render(response):
    """Render a SQL query response as a formatted table 
    or status message."""
    
    if isinstance(response, str):
       response = json.loads(response)
   
    if not response.get("ok", False):
        return "SQL error: " + response.get("error", "Unknown error")

   
    cols = response.get("columns", [])
    rows = response.get("rows", [])
    execution_time_ms = response.get("execution_time", 0) * 1000

    if not cols:
        return f"OK ({response.get('rows_affected', 0)} rows affected)"

    column_widths = [len(str(c)) for c in cols]

    for r in rows:
        for i, v in enumerate(r):
            column_widths[i] = max(
                column_widths[i],
                len(format_value(v))
            )
            
    out = []

    out.append(
        "  ".join(
            str(c).ljust(column_widths[i])
            for i, c in enumerate(cols)
        )
    )

    out.append(
        "  ".join("-" * width for width in column_widths)
    )

    for r in rows:
        out.append(
            "  ".join(
                format_value(v, column_widths[i])
                for i, v in enumerate(r)
            )
        )

    out.append("")
    out.append(
        f"{len(rows)} row{'s' if len(rows) != 1 else ''} returned "
        f"({execution_time_ms:.2f} ms)"
    )

    return "\n".join(out)
