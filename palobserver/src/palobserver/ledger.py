import sqlite3, json, pathlib

LEDGER_PATH = pathlib.Path.home() / ".pal_ledger.db"
_DDL = """
CREATE TABLE IF NOT EXISTS ledger (
    bundle_id   TEXT PRIMARY KEY,
    created     TEXT,
    conflict_ct INTEGER,
    bundle_json TEXT
);
"""

def _db():
    conn = sqlite3.connect(LEDGER_PATH)
    conn.execute(_DDL)
    return conn

def write(bundle: dict):
    conflict_ct = sum(len(s["flags"]) for s in bundle["shards"])
    with _db() as db:
        db.execute(
            "INSERT OR IGNORE INTO ledger VALUES (?,?,?,?)",
            (
                bundle["bundle_id"],
                bundle["created"],
                conflict_ct,
                json.dumps(bundle),
            ),
        )

