"""CSV loading for results files. Uses the stdlib csv module instead of the
original's hand-rolled regex splitter, so quoted fields containing commas
are handled correctly.

Expected columns (no header semantics are relied on, just position):
  0: position/place
  1: player name
  2: points
  3: army name
  4: army ID (optional, may be blank)
"""
import csv


def load_results_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)  # header row
        return [row for row in reader if any(cell.strip() for cell in row)]
