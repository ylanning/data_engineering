from airflow import DAG
import pendulum
from datetime import timedelta, datetime
from api.video_stats import (
    get_playlist_id,
    get_playlist_items,
    save_stats_to_json,
    extract_video_stats,
)

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
