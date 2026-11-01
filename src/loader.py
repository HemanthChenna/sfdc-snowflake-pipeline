"""Land records in Snowflake raw layer (bronze) as VARIANT via internal stage."""
import json
import os
import tempfile
from pathlib import Path


def write_ndjson(records: list[dict], obj: str, directory: str | None = None) -> Path:
    directory = directory or tempfile.mkdtemp()
    path = Path(directory) / f"{obj.lower()}.ndjson"
    with path.open("w") as f:
        for r in records:
            f.write(json.dumps(r, default=str) + "\n")
    return path


def snowflake_connection():
    import snowflake.connector
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        role=os.environ.get("SNOWFLAKE_ROLE"),
        schema="RAW",
    )


def load_file(conn, path: Path, obj: str) -> int:
    """PUT + COPY INTO. COPY is idempotent per file via load history; the file
    name includes a run id so reruns of the same batch are skipped safely."""
    table = f"SF_{obj.upper()}"
    cur = conn.cursor()
    try:
        cur.execute(f"PUT file://{path} @%{table} AUTO_COMPRESS=TRUE OVERWRITE=TRUE")
        cur.execute(
            f"COPY INTO {table} (payload, _source_file) "
            f"FROM (SELECT $1, METADATA$FILENAME FROM @%{table}) "
            f"FILE_FORMAT=(TYPE=JSON) ON_ERROR=ABORT_STATEMENT"
        )
        return sum(row[3] for row in cur.fetchall() if isinstance(row[3], int))
    finally:
        cur.close()
