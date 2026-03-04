from .data_extractions import insert_rows, update_rows, delete_rows
from .data_transformation import transform_data
from .data_loading import load_data
from .data_transformation import transform_data
from .data_utils import (
    get_conn_cursor,
    close_conn_cursor,
    create_schema,
    create_table,
    get_video_ids_from_db,
)

import logging
from airflow.decorators import task

logger = logging.getLogger(__name__)
table = "youtube_video_stats"


@task
def staging_table():
    schema = "staging"
    conn, cur = None, None

    try:
        conn, cur = get_conn_cursor()

        youtube_data = load_data()
        create_schema(schema)
        create_table(schema, table)

        table_ids = get_video_ids_from_db(cur, schema)

        for row in youtube_data:
            if len(table_ids) == 0 or row["video_id"] not in table_ids:
                insert_rows(cur, conn, schema, [row])
            elif row["video_id"] in table_ids:
                update_rows(cur, conn, schema, [row])

        ids_in_json = {row["video_id"] for row in youtube_data}

        video_ids_to_be_deleted = set(table_ids) - ids_in_json

        if video_ids_to_be_deleted:
            delete_rows(cur, conn, schema, video_ids_to_be_deleted)

        logger.info("Staging table created successfully.")
    except Exception as e:
        logger.error(f"Error in staging_table task: {e}")
        raise e
    finally:
        if conn and cur:
            close_conn_cursor(conn, cur)


def core_table():

    schema = "core"
    conn, cur = None, None

    try:
        conn, cur = get_conn_cursor()
        create_schema(schema)
        create_table(schema, table)

        table_ids = get_video_ids_from_db(cur, schema)
        current_video_ids = set()

        cur.execute(f"SELECT * FROM staging.{table};")
        rows = cur.fetchall()

        for row in rows:

            current_video_ids.add(row["video_id"])
            if len(table_ids) == 0 or row["video_id"] not in table_ids:
                insert_rows(cur, conn, schema, [row])
            elif row["video_id"] in table_ids:
                update_rows(cur, conn, schema, [row])

        video_ids_to_be_deleted = set(table_ids) - current_video_ids

        if video_ids_to_be_deleted:
            delete_rows(cur, conn, schema, video_ids_to_be_deleted)

        logger.info("Core table created successfully.")

    except Exception as e:
        logger.error(f"Error in core_table task of {schema} schema: {e}")
        raise e
    finally:
        if conn and cur:
            close_conn_cursor(conn, cur)
