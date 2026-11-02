"""Convert MeG Army Builder 'INPUT SHEET' spreadsheets into JSON.

The MeG Army Builder workbook has three tabs: an instructions tab, an
'INPUT SHEET' tab (where the player fills in generals and units), and a
'PRINT FORMAT' tab (a formatted read-out of the same data). This script
reads only the 'INPUT SHEET' tab and pulls out the fields the player
actually enters -- army identity, generals, the "set up" summary numbers,
and the unit roster -- skipping the sheet's CALCULATION ZONE (columns Y
onward), which is internal formula scratch space for the points engine.

The unit table's column order has drifted between yearly versions of the
workbook (e.g. 'Melee Weapon' and 'SHOOTING' swap places), so columns are
located by matching the header text in row 10/11 rather than by fixed
column letters. Rows 1-9 (army info, generals, set up) have stayed at
fixed positions across the versions checked (2020-2025) and are read
directly.

Usage:
    python xlsx_army_list_to_json.py <input.xlsx> [-o output.json]
    python xlsx_army_list_to_json.py --batch <folder> [--out-dir <folder>]
"""
import argparse
import json
import os
import sys
from datetime import date, datetime

import openpyxl

INPUT_TAB_NAME = "INPUT SHEET"

# Row 10 header labels (normalised) that belong to the player-input unit
# table. Anything else in row 10 (e.g. 'TABLE OFFSET') is CALCULATION ZONE
# and is deliberately ignored.
UNIT_HEADER_KEYS = {
    "ug no": "ug_no",
    "name": "name",
    "type": "type",
    "training & formation": "training_and_formation",
    "quality": "quality",
    "armour": "armour",
    "shooting": "shooting",
    "melee weapon": "melee_weapon",
    "special characteristics": "special_characteristics",
    "number of bases": "bases",
    "points per base": "points_per_base",
    "points total": "points_total",
    "break on *": "break_on",
    "scout contrib": "scout_contribution",
}

GENERAL_HEADER_KEYS = {
    "general": "role",
    "name": "name",
    "type": "type",
    "ally?": "ally",
    "pts": "points",
    "c&c cards": "cc_cards",
}


def norm(value):
    if value is None:
        return ""
    return " ".join(str(value).strip().split()).lower()


def cell_value(ws, row, col):
    if col is None:
        return None
    v = ws.cell(row=row, column=col).value
    if isinstance(v, datetime):
        return v.date().isoformat()
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, str):
        v = v.strip()
        return v if v != "" else None
    return v


def find_label_col(ws, row, label, max_col=30):
    for c in range(1, max_col + 1):
        if norm(ws.cell(row=row, column=c).value) == label:
            return c
    return None


def parse_army_info(ws):
    army_col = find_label_col(ws, 1, "army")
    date_col = find_label_col(ws, 1, "date")
    allies_col = find_label_col(ws, 1, "allies")
    pbs_col = find_label_col(ws, 1, "pbs terrain maps")
    army_no_col = find_label_col(ws, 1, "army no.")
    army_book_col = find_label_col(ws, 1, "army book list")
    player_col = find_label_col(ws, 1, "player")
    contact_col = find_label_col(ws, 1, "contact details")

    info = {
        "army_name": cell_value(ws, 2, army_col),
        "date": cell_value(ws, 2, date_col),
        "allies": cell_value(ws, 2, allies_col),
        "army_no": cell_value(ws, 2, army_no_col),
        "army_book_list": cell_value(ws, 2, army_book_col),
        "player": cell_value(ws, 2, player_col),
        "contact_details": cell_value(ws, 2, contact_col),
        "issue": cell_value(ws, 3, 12),  # L3, fixed position across versions
    }

    if pbs_col:
        following = [c for c in (army_no_col, army_book_col, player_col, contact_col)
                     if c and c > pbs_col]
        stop_col = min(following) if following else pbs_col + 3
        terrain = [cell_value(ws, 2, c) for c in range(pbs_col, stop_col)]
        info["pbs_terrain_maps"] = [t for t in terrain if t not in (None, "-")]
    else:
        info["pbs_terrain_maps"] = []

    return info


def parse_generals(ws):
    header_cols = {}
    for c in range(1, 14):
        label = norm(ws.cell(row=4, column=c).value)
        if label in GENERAL_HEADER_KEYS:
            header_cols[GENERAL_HEADER_KEYS[label]] = c

    generals = []
    for row in range(5, 9):
        role = cell_value(ws, row, header_cols.get("role"))
        name = cell_value(ws, row, header_cols.get("name"))
        if role is None and name is None:
            continue
        generals.append({
            "role": role,
            "name": name,
            "type": cell_value(ws, row, header_cols.get("type")),
            "ally": cell_value(ws, row, header_cols.get("ally")),
            "points": cell_value(ws, row, header_cols.get("points")),
            "cc_cards": cell_value(ws, row, header_cols.get("cc_cards")),
        })
    return generals


def parse_setup(ws):
    # Fixed positions across the versions checked (2020-2025).
    return {
        "pbs_map_cards": cell_value(ws, 4, 16),        # P4
        "scouting_cards": cell_value(ws, 5, 16),       # P5
        "tugs_to_break": cell_value(ws, 6, 16),        # P6
        "ugs_total": cell_value(ws, 7, 11),            # K7
        "deployment_per_batch": cell_value(ws, 8, 11), # K8
        "points_total": cell_value(ws, 8, 16),         # P8
    }


def _unit_header_spans(ws):
    """Map each whitelisted row-10 header to the column range it owns,
    by looking only at whitelisted labels and using the next whitelisted
    label's column as the boundary. This keeps the CALCULATION ZONE
    (unwhitelisted headers further right) from bleeding into the last
    real column (Scout contrib)."""
    found = []
    for c in range(1, ws.max_column + 1):
        label = norm(ws.cell(row=10, column=c).value)
        if label in UNIT_HEADER_KEYS:
            found.append((c, label))
    found.sort()

    spans = {}
    for i, (col, label) in enumerate(found):
        end = found[i + 1][0] - 1 if i + 1 < len(found) else col
        spans[label] = (col, end)
    return spans


def parse_units(ws):
    spans = _unit_header_spans(ws)
    name_col = spans.get("name", (2, 2))[0]

    units = []
    row = 12
    while row <= ws.max_row:
        marker = ws.cell(row=row, column=1).value
        if isinstance(marker, str) and marker.strip().upper() == "DATA":
            break

        name_val = cell_value(ws, row, name_col)
        if name_val is not None:
            unit = {}
            for label, (c0, c1) in spans.items():
                key = UNIT_HEADER_KEYS[label]
                if label == "shooting":
                    unit[key] = {
                        "skill": cell_value(ws, row, c0),
                        "weapon": cell_value(ws, row, c0 + 1) if c1 > c0 else None,
                    }
                elif label == "special characteristics":
                    vals = [cell_value(ws, row, c) for c in range(c0, c1 + 1)]
                    unit[key] = [v for v in vals if v not in (None, "-")]
                else:
                    unit[key] = cell_value(ws, row, c0)
            units.append(unit)
        row += 1
    return units


def convert_workbook(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    if INPUT_TAB_NAME not in wb.sheetnames:
        raise ValueError(f"no '{INPUT_TAB_NAME}' tab (sheets: {wb.sheetnames})")
    ws = wb[INPUT_TAB_NAME]

    return {
        "source_file": os.path.basename(path),
        "army_info": parse_army_info(ws),
        "generals": parse_generals(ws),
        "setup": parse_setup(ws),
        "units": parse_units(ws),
    }


def convert_file(in_path, out_path=None):
    data = convert_workbook(in_path)
    if out_path is None:
        out_path = os.path.splitext(in_path)[0] + ".json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return out_path


def batch_convert(folder, out_dir=None):
    converted, skipped, failed = [], [], []
    for dirpath, _dirnames, filenames in os.walk(folder):
        for fname in filenames:
            if not fname.lower().endswith(".xlsx") or fname.startswith("~$"):
                continue
            in_path = os.path.join(dirpath, fname)
            try:
                data = convert_workbook(in_path)
            except ValueError:
                skipped.append(in_path)
                continue
            except Exception as exc:
                failed.append((in_path, str(exc)))
                continue

            if out_dir:
                rel = os.path.relpath(dirpath, folder)
                dest_dir = os.path.join(out_dir, rel) if rel != "." else out_dir
                os.makedirs(dest_dir, exist_ok=True)
                out_path = os.path.join(dest_dir, os.path.splitext(fname)[0] + ".json")
            else:
                out_path = os.path.splitext(in_path)[0] + ".json"

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            converted.append(out_path)

    return converted, skipped, failed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="path to a single .xlsx file")
    parser.add_argument("-o", "--output", help="output .json path (single-file mode)")
    parser.add_argument("--batch", metavar="FOLDER", help="recursively convert every .xlsx in FOLDER")
    parser.add_argument("--out-dir", metavar="FOLDER", help="output folder for --batch (mirrors input tree); defaults to next to each source file")
    args = parser.parse_args()

    if args.batch:
        converted, skipped, failed = batch_convert(args.batch, args.out_dir)
        print(f"Converted {len(converted)} file(s).")
        if skipped:
            print(f"Skipped {len(skipped)} file(s) without an '{INPUT_TAB_NAME}' tab:")
            for p in skipped:
                print(f"  - {p}")
        if failed:
            print(f"Failed on {len(failed)} file(s):")
            for p, err in failed:
                print(f"  - {p}: {err}")
        return

    if not args.input:
        parser.error("provide an input .xlsx path, or use --batch FOLDER")

    out_path = convert_file(args.input, args.output)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
