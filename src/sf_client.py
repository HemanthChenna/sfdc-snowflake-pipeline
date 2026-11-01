"""Salesforce extraction: incremental SOQL on SystemModstamp."""
import os
from typing import Iterator


def connect():
    from simple_salesforce import Salesforce  # lazy import keeps tests light
    if os.environ.get("SF_ACCESS_TOKEN"):     # OAuth session (recommended)
        return Salesforce(instance_url=os.environ["SF_INSTANCE_URL"],
                          session_id=os.environ["SF_ACCESS_TOKEN"])
    return Salesforce(
        username=os.environ["SF_USERNAME"],
        password=os.environ["SF_PASSWORD"],
        security_token=os.environ["SF_SECURITY_TOKEN"],
        domain=os.environ.get("SF_DOMAIN", "login"),
    )


def build_soql(obj: str, fields: list[str], since: str) -> str:
    """Incremental query. >= plus idempotent downstream dedup means no gaps."""
    return (
        f"SELECT {', '.join(fields)} FROM {obj} "
        f"WHERE SystemModstamp >= {since} ORDER BY SystemModstamp ASC"
    )


def extract(sf, obj: str, fields: list[str], since: str) -> Iterator[dict]:
    """include_deleted=True uses queryAll, so deleted records are captured."""
    for rec in sf.query_all_iter(build_soql(obj, fields, since), include_deleted=True):
        rec.pop("attributes", None)
        yield rec


def fetch_pipeline_summary(sf) -> list[dict]:
    """Call the custom Apex REST endpoint (see apex/classes)."""
    return sf.apexecute("pipeline-summary", method="GET")
