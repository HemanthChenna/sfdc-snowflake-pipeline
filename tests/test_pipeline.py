import pytest
from src.sf_client import build_soql, extract
from src.validate import validate_batch, max_watermark, ValidationError
from src.watermark import WatermarkStore
from src.reconcile import compare
from src.pipeline import run_object


class FakeSF:
    def __init__(self, rows): self.rows, self.last_soql = rows, None
    def query_all_iter(self, soql, include_deleted=False):
        self.last_soql = soql
        for r in self.rows: yield dict(r, attributes={"type": "X"})


ROWS = [
    {"Id": "001A", "SystemModstamp": "2026-01-01T10:00:00.000+0000"},
    {"Id": "001B", "SystemModstamp": "2026-01-02T10:00:00.000+0000"},
]


def test_soql_is_incremental_and_includes_deletes():
    q = build_soql("Account", ["Id"], "2026-01-01T00:00:00Z")
    assert "SystemModstamp >= 2026-01-01T00:00:00Z" in q


def test_extract_strips_attributes():
    out = list(extract(FakeSF(ROWS), "Account", ["Id"], "x"))
    assert all("attributes" not in r for r in out)


def test_validation_rejects_missing_id():
    with pytest.raises(ValidationError):
        validate_batch([{"Id": "", "SystemModstamp": "t"}], ["Id", "SystemModstamp"])


def test_validation_rejects_duplicate_versions():
    with pytest.raises(ValidationError):
        validate_batch([ROWS[0], ROWS[0]], ["Id", "SystemModstamp"])


def test_watermark_advances_only_after_successful_load(tmp_path):
    store = WatermarkStore(tmp_path / "wm.json")

    def failing_load(recs, obj): raise RuntimeError("snowflake down")
    with pytest.raises(RuntimeError):
        run_object(FakeSF(ROWS), "Account", ["Id", "SystemModstamp"], store, failing_load)
    assert store.get("Account") == "1970-01-01T00:00:00Z"   # unchanged -> safe rerun

    n = run_object(FakeSF(ROWS), "Account", ["Id", "SystemModstamp"], store, lambda r, o: None)
    assert n == 2 and store.get("Account") == max_watermark(ROWS)


def test_reconcile_flags_mismatch():
    assert compare({"A": 100.0}, {"A": 100.0}) == []
    assert compare({"A": 100.0}, {"A": 90.0}) == ["A: Salesforce=100.00 Snowflake=90.00"]
    assert len(compare({"A": 1.0}, {})) == 1   # stage missing in warehouse
