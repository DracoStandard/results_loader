"""Database access layer, talking to the same SQL Server 'rankings' DB the
C# version used (see ../ResultsLoaderV2/DataClasses1.dbml for the original
schema/stored-proc definitions).
"""
import os

import pyodbc
from dotenv import load_dotenv

load_dotenv()

_conn = None


def get_connection():
    global _conn
    if _conn is None:
        driver = os.environ.get("DB_DRIVER", "ODBC Driver 17 for SQL Server")
        server = os.environ["DB_SERVER"]
        database = os.environ["DB_NAME"]
        user = os.environ["DB_USER"]
        password = os.environ["DB_PASSWORD"]
        conn_str = (
            f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};"
            f"UID={user};PWD={password};TrustServerCertificate=yes"
        )
        _conn = pyodbc.connect(conn_str, autocommit=True)
    return _conn


def _fetch_output_guid(cur):
    """Advance to the first query result set and return the first column."""
    while cur.description is None:
        if not cur.nextset():
            return None
    row = cur.fetchone()
    return str(row[0]) if row and row[0] else None


def add_comp(comp_name, comp_date, player_count, max_points, sys_name):
    """Calls dracostandard.addComp, returns the new CompID as a string."""
    sql = """
        DECLARE @outID UNIQUEIDENTIFIER;
        EXEC dracostandard.addComp
            @CompName = ?, @CompDate = ?, @noOfPlayers = ?,
            @MaxPoints = ?, @sys = ?, @returnCompID = @outID OUTPUT;
        SELECT @outID;
    """
    cur = get_connection().cursor()
    cur.execute(sql, (comp_name, comp_date, player_count, max_points, sys_name))
    return _fetch_output_guid(cur)


def add_player(name):
    """Calls dracostandard.addPlayer, returns the new PlayerID as a string."""
    sql = """
        DECLARE @outID UNIQUEIDENTIFIER;
        EXEC dracostandard.addPlayer
            @playerName = ?, @returnID = @outID OUTPUT;
        SELECT @outID;
    """
    cur = get_connection().cursor()
    cur.execute(sql, (name,))
    return _fetch_output_guid(cur)


def add_placing(position, name, army, score, points, comp_id, player_id, army_id):
    sql = """
        EXEC dracostandard.addPlacing
            @position = ?, @name = ?, @army = ?, @score = ?,
            @points = ?, @comp = ?, @playerID = ?, @armyID = ?;
    """
    cur = get_connection().cursor()
    cur.execute(
        sql, (position, name, army, score, points, comp_id, player_id, army_id)
    )


def find_player_by_name(name):
    cur = get_connection().cursor()
    cur.execute("SELECT PlayerID, Name FROM dbo.players WHERE Name = ?", (name,))
    row = cur.fetchone()
    return (str(row.PlayerID), row.Name) if row else None


def list_players():
    cur = get_connection().cursor()
    cur.execute("SELECT PlayerID, Name FROM dbo.players")
    return [(str(r.PlayerID), r.Name) for r in cur.fetchall() if r.Name]


def find_army_by_name(name):
    cur = get_connection().cursor()
    cur.execute("SELECT No, Army FROM dracostandard.ArmyIndex WHERE Army = ?", (name,))
    row = cur.fetchone()
    return (row.No, row.Army) if row else None


def list_armies():
    cur = get_connection().cursor()
    cur.execute("SELECT No, Army FROM dracostandard.ArmyIndex")
    return [(r.No, r.Army) for r in cur.fetchall()]


def placings_with_bad_army_id():
    cur = get_connection().cursor()
    cur.execute("SELECT comp, PlayerID, army, ArmyID FROM dbo.placings WHERE ArmyID = '0'")
    return cur.fetchall()


def update_placing_army_id(comp_id, player_id, new_army_id):
    cur = get_connection().cursor()
    cur.execute(
        "UPDATE dbo.placings SET ArmyID = ? WHERE comp = ? AND PlayerID = ?",
        (new_army_id, comp_id, player_id),
    )


def exec_update_old_comps():
    get_connection().cursor().execute("EXEC updateOldComps")
