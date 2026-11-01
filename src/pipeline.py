"""Extract -> validate -> land -> advance watermark (only after successful load)."""
import logging
from src.config import OBJECTS, REQUIRED_FIELDS
from src.sf_client import extract
from src.validate import validate_batch, max_watermark
from src.watermark import WatermarkStore

log = logging.getLogger("sfdc_pipeline")


def run_object(sf, obj, fields, store, load_fn) -> int:
    since = store.get(obj)
    records = list(extract(sf, obj, fields, since))
    log.info("%s: extracted %d rows since %s", obj, len(records), since)
    if not records:
        return 0
    validate_batch(records, REQUIRED_FIELDS)
    load_fn(records, obj)                      # raises on failure -> watermark untouched
    store.set(obj, max_watermark(records))     # advance only after success
    return len(records)


def run(sf, store, load_fn) -> dict[str, int]:
    return {obj: run_object(sf, obj, fields, store, load_fn)
            for obj, fields in OBJECTS.items()}


if __name__ == "__main__":
    from dotenv import load_dotenv
    from src.sf_client import connect
    from src.loader import write_ndjson, snowflake_connection, load_file

    load_dotenv()
    logging.basicConfig(level=logging.WARNING); logging.getLogger("snowflake").setLevel(logging.ERROR); logging.getLogger("sfdc_pipeline").setLevel(logging.INFO)
    conn = snowflake_connection()

    def _load(records, obj):
        load_file(conn, write_ndjson(records, obj), obj)

    print(run(connect(), WatermarkStore(), _load))
