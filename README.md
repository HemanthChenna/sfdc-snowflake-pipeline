# Salesforce → Snowflake Data Pipeline (with Apex reconciliation)

Incremental ELT pipeline that extracts Account and Opportunity data from Salesforce,
lands it in Snowflake (medallion layers), models it with dbt, orchestrates it with
Airflow, and reconciles results against a custom **Apex REST endpoint**.

## Architecture
```
Salesforce (Account, Opportunity)
   │  SOQL on SystemModstamp (incremental, includes deletes)
   ▼
Python (simple-salesforce) ── validate ──► NDJSON ──► Snowflake RAW (bronze, VARIANT)
                                                         │ dbt incremental + dedup
                                                         ▼
                                              STAGING (silver) ──► MARTS (gold)
                                                                       │
Apex REST  GET /services/apexrest/pipeline-summary ◄── reconcile ──────┘
Airflow: extract_and_load → dbt source freshness → dbt run → dbt test
```

## Design decisions (good interview material)
- **Incremental by SystemModstamp**, `>=` plus downstream dedup, so no gaps and safe reruns.
- **Watermark advances only after a successful load**, so failures never skip data.
- **ALL ROWS** captures soft-deleted records; marts filter on `is_deleted`.
- **Bronze keeps raw VARIANT**, which tolerates Salesforce schema changes; typing happens in dbt.
- **Validation before landing** (required fields, duplicate versions).
- **Reconciliation** against Apex aggregate SOQL, an independent source-of-truth check.
- **dbt tests + source freshness** and Airflow retries with backoff and a task SLA.
- Least-privilege Snowflake loader role (`sql/01_snowflake_setup.sql`).

## Setup
1. **Salesforce:** create a free Developer Edition org at developer.salesforce.com/signup.
   Get your security token (Settings → Reset My Security Token). The dev org includes sample Accounts/Opportunities; add a few more.
2. **Apex:** deploy `apex/classes/*` via Developer Console or VS Code + Salesforce CLI
   (`sf project deploy start`). Run the test class and confirm it passes.
3. **Snowflake:** free trial → run `sql/01_snowflake_setup.sql`.
4. `cp .env.example .env`, fill it in, `pip install -r requirements.txt`.
5. Run `python -m src.pipeline`, then `cd dbt && dbt run && dbt test`.
6. Optional: run the DAG in `airflow/dags/` (Docker or Astro CLI).
7. Unit tests: `pytest` (no credentials needed).

## Status
- Unit tests (extraction query, validation, watermark/failure behaviour, reconciliation) pass locally.
- Salesforce, Snowflake, dbt, Apex and Airflow pieces need to be run against your own accounts.
