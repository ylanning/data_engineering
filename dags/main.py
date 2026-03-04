from airflow import DAG
import pendulum
from datetime import timedelta, datetime
from api.video_stats import (
    get_playlist_id,
    get_playlist_items,
    save_stats_to_json,
    extract_video_stats,
)

from datawarehouse.data_warehouse import staging_table, core_table
from dataquality.soda import yt_elt_data_quality

# Default Args
default_args = {
    "owner": "data engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "yanti.lanning@gmail.com",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "max_active_runs": 1,
    "dagrun_timeout": timedelta(minutes=60),
    "start_date": datetime(2025, 1, 1, tzinfo=pendulum.timezone("UTC")),
    "end_date": None,
}

# Variables
staging_schema = "staging"
core_schema = "core"

with DAG(
    dag_id="import_json",
    default_args=default_args,
    description="A DAG to generate a JSON file with raw data from the YouTube API",
    schedule="0 14 * * *",
    catchup=False,
) as dag:

    # Tasks
    playlist_id = get_playlist_id()
    video_ids = get_playlist_items(playlist_id)
    extracted_stats = extract_video_stats(video_ids)
    save_to_json = save_stats_to_json(extracted_stats)

    # Task dependencies
    playlist_id >> video_ids >> extracted_stats >> save_to_json

with DAG(
    dag_id="update_db",
    default_args=default_args,
    description="A DAG to update the staging and core tables in the Postgres database with the latest data from the YouTube API",
    schedule="0 15 * * *",
    catchup=False,
) as dag:

    # Tasks
    update_staging = staging_table()
    update_core = core_table()

    # Task dependencies
    update_staging >> update_core


with DAG(
    dag_id="data_quality_checks",
    default_args=default_args,
    description="A DAG to perform data quality checks on the staging and core tables in the Postgres database",
    schedule="0 16 * * *",
    catchup=False,
) as dag:

    # Tasks
    soda_validate_staging = yt_elt_data_quality(staging_schema)
    soda_validate_core = yt_elt_data_quality(core_schema)

    # Task dependencies
    soda_validate_staging >> soda_validate_core
