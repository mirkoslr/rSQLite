"""
rSQLite result exporter.

Responsibilities:
- Export SQL query results to CSV, JSON, and TXT files
"""

import csv
import json

from rsqlite import formatter

def export_csv(result, output_file):
    """Export query results to a CSV file."""
    columns = result["columns"]
    rows = result["rows"]

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(rows)


def export_json(result, output_file):
    """Export query results to a JSON file."""
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)


def export_txt(result, output_file):
    """Export formatted query results to a text file."""
    text = formatter.render(result)

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(text)
        