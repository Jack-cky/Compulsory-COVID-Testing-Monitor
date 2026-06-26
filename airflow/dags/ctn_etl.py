from datetime import timedelta

import pendulum
from airflow.sdk import Variable, dag, task


@dag(
    dag_id="ctn_etl",
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
        "execution_timeout": timedelta(minutes=5),
        "retry_exponential_backoff": True,
    },
    schedule="0 1 * * *",
    start_date=pendulum.datetime(2022, 1, 11, tz="Asia/Hong_Kong"),
    catchup=True,
    max_active_runs=1,
    tags=["ctn", "etl"],
)
def ctn_etl():
    @task
    def setup_task() -> None:
        from ctn_monitor.etl.path_setup import initialise_paths

        initialise_paths()

    @task(retries=2, retry_delay=timedelta(minutes=3))
    def download_task(logical_date=None) -> str:
        from ctn_monitor.etl.download import download_chp_ctn

        return download_chp_ctn(logical_date.strftime("%Y%m%d"))

    @task(retries=2, retry_delay=timedelta(minutes=3))
    def extract_task(ctn: str) -> str:
        from ctn_monitor.etl.extract import extract_pdf_table

        return extract_pdf_table(
            ctn,
            client_id=Variable.get("CLIENT_ID"),
            client_secret=Variable.get("CLIENT_SECRET"),
        )

    @task
    def tabular_task(ctn: str) -> str:
        from ctn_monitor.etl.tabulate import tabulate_zipped_excel

        return tabulate_zipped_excel(ctn)

    @task
    def geocode_task(ctn: str) -> None:
        from ctn_monitor.etl.geocode import geocode_tab_address

        geocode_tab_address(ctn)

    @task
    def model_task() -> None:
        from ctn_monitor.etl.model import build_model

        build_model()

    setup = setup_task()
    download = download_task()
    extract = extract_task(download)
    tabular = tabular_task(extract)
    geocode = geocode_task(tabular)
    model = model_task()

    setup >> download >> extract >> tabular >> geocode >> model


ctn_etl()
