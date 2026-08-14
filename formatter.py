import json


def format_value(value, width=None):
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

    # The transport layer normally returns a str.
    # Keep support for bytes in case a raw Reticulum response is passed here.
    if isinstance(response, bytes):
        response = response.decode()

    if isinstance(response, str):
        response = json.loads(response)

    if not response.get("ok", False):
        return "SQL error: " + response.get("error", "Unknown error")

    # Extract columns, rows, and execution time from the query response.
    cols = response.get("columns", [])
    rows = response.get("rows", [])
    execution_time_ms = response.get("execution_time", 0) * 1000

    # If there are no columns, the query did not return a result set.
    if not cols:
        return f"OK ({response.get('rows_affected', 0)} rows affected)"

    # Start each column width with the length of its column name.
    column_widths = [len(str(c)) for c in cols]

    # Expand each column width to fit the longest value in that column.
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
