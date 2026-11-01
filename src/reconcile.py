"""Reconcile Apex summary (source of truth) vs. Snowflake mart totals."""


def compare(sf_summary: dict[str, float], warehouse: dict[str, float],
            tolerance: float = 0.01) -> list[str]:
    """Both args map StageName -> total open Amount. Returns list of problems."""
    problems = []
    for stage in sorted(set(sf_summary) | set(warehouse)):
        s, w = sf_summary.get(stage, 0.0), warehouse.get(stage, 0.0)
        if abs(s - w) > tolerance:
            problems.append(f"{stage}: Salesforce={s:,.2f} Snowflake={w:,.2f}")
    return problems
