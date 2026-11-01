from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

DBT = "cd /opt/project/dbt && dbt"

def _ingest():
    from src.pipeline import run
    from src.sf_client import connect
    from src.loader import write_ndjson, snowflake_connection, load_file
    from src.watermark import WatermarkStore
    conn = snowflake_connection()
    return run(connect(), WatermarkStore(),
               lambda recs, obj: load_file(conn, write_ndjson(recs, obj), obj))

with DAG(
    "sfdc_to_snowflake",
    start_date=datetime(2025, 1, 1),
    schedule="0 5 * * *",            # daily 05:00, ahead of business hours
    catchup=False,
    default_args={"retries": 3, "retry_delay": timedelta(minutes=5),
                  "retry_exponential_backoff": True},
    sla_miss_callback=None,
) as dag:
    ingest = PythonOperator(task_id="extract_and_load", python_callable=_ingest,
                            sla=timedelta(hours=1))
    freshness = BashOperator(task_id="dbt_source_freshness", bash_command=f"{DBT} source freshness")
    run_models = BashOperator(task_id="dbt_run", bash_command=f"{DBT} run")
    test_models = BashOperator(task_id="dbt_test", bash_command=f"{DBT} test")

    ingest >> freshness >> run_models >> test_models
