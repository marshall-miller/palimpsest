import click, json, sqlite3, pathlib, datetime

LEDGER = pathlib.Path.home() / ".pal_ledger.db"

@click.group()
def pal():
    """Palimpsest command-line utility."""
    pass

@pal.group()
def ledger():
    """Ledger sub-commands."""
    pass

@ledger.command(name="ls")
@click.option("--limit", default=5, help="Rows to display")
def ls_cmd(limit):
    conn = sqlite3.connect(LEDGER)
    rows = conn.execute(
        "SELECT bundle_id, created, conflict_ct FROM ledger "
        "ORDER BY created DESC LIMIT ?", (limit,)
    )
    for b, ts, ct in rows.fetchall():
        ts = datetime.datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{ts}  {b[:8]}…  conflicts={ct}")

@ledger.command(name="show")
@click.argument("bundle_id")
def show_cmd(bundle_id):
    conn = sqlite3.connect(LEDGER)
    row = conn.execute(
        "SELECT bundle_json FROM ledger WHERE bundle_id=?",
        (bundle_id,),
    ).fetchone()
    if not row:
        click.echo("Bundle not found")
        return
    print(json.dumps(json.loads(row[0]), indent=2)[:1000])

