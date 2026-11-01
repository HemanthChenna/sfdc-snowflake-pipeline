"""Pre-load data quality checks. Fail fast so bad data never lands."""


class ValidationError(Exception):
    pass


def validate_batch(records: list[dict], required: list[str]) -> None:
    if not records:
        return
    seen = set()
    for i, r in enumerate(records):
        missing = [f for f in required if r.get(f) in (None, "")]
        if missing:
            raise ValidationError(f"Row {i} missing required fields {missing}")
        key = (r["Id"], r["SystemModstamp"])
        if key in seen:
            raise ValidationError(f"Duplicate record version in batch: {key}")
        seen.add(key)


def max_watermark(records: list[dict]) -> str | None:
    return max((r["SystemModstamp"] for r in records), default=None)
