"""Core workflow, ported from compResults.cs: create a competition, resolve
each row's player/army to a database ID (exact match, then fuzzy-match
picker, then create-new for players), and record each placing.
"""
import db
import matcher
import picker_dialog


def determine_max_points(player_count):
    if player_count >= 20:
        return 25
    if player_count >= 14:
        return 20
    if player_count >= 10:
        return 15
    return 10


def get_army_id(parent, army_name):
    if not army_name:
        return ""

    exact = db.find_army_by_name(army_name)
    if exact:
        return str(exact[0])

    candidates = db.list_armies()
    matches = matcher.top_matches(army_name, candidates) if candidates else []
    if not matches:
        return ""

    chosen = picker_dialog.ask_pick(parent, army_name, matches, id_header="No", label_header="Army")
    return chosen or ""


def get_player_id(parent, player_name):
    exact = db.find_player_by_name(player_name)
    if exact:
        return exact[0]

    candidates = db.list_players()
    matches = matcher.top_matches(player_name, candidates) if candidates else []
    if matches:
        chosen = picker_dialog.ask_pick(
            parent, player_name, matches, id_header="PlayerID", label_header="Name"
        )
        if chosen:
            return chosen

    return db.add_player(player_name)


def process_results_csv(parent, comp_name, comp_date, system, is_major, rows):
    """rows: list of CSV data rows (see csv_loader.load_results_csv).
    Returns (processed_count, skipped_count).
    """
    player_count = len(rows)
    if is_major:
        player_count += 6
    max_points = determine_max_points(player_count)

    comp_id = db.add_comp(comp_name, comp_date, player_count, max_points, system)

    processed = 0
    skipped = 0
    for row in rows:
        try:
            position = int(row[0])
        except (ValueError, IndexError):
            skipped += 1
            continue

        player_name = row[1] if len(row) > 1 else ""
        try:
            points = int(row[2])
        except (ValueError, IndexError):
            points = 0
        army_name = row[3] if len(row) > 3 else ""
        army_id = row[4].strip() if len(row) > 4 else ""

        player_id = get_player_id(parent, player_name)

        if not army_id:
            army_id = get_army_id(parent, army_name)

        if system == "REG":
            army_id = ""

        # NB: proc signature is (position, name, army, score, points, ...) -
        # the original passes the parsed points as "score" and leaves
        # "points" blank, so we mirror that here.
        db.add_placing(position, player_name, army_name, str(points), "", comp_id, player_id, army_id)
        processed += 1

    return processed, skipped


def fix_incorrect_army_ids(parent):
    """Re-resolves placings whose ArmyID is '0', ported from
    compResults.FixIncorrectArmyIDs. Returns the number of rows updated.
    """
    fixed = 0
    for row in db.placings_with_bad_army_id():
        correct = get_army_id(parent, row.army)
        if correct and correct != str(row.ArmyID):
            db.update_placing_army_id(row.comp, row.PlayerID, correct)
            fixed += 1
    return fixed
