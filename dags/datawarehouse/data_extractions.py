import logging

logger = logging.getLogger(__name__)
TABLE = "youtube_video_stats"
VALID_SCHEMAS = {"staging", "core"}

# Map JSON keys to database column names
JSON_TO_DB_COLUMN = {
    "title": "video_title",
}


def _transform_row(row: dict) -> dict:
    """Transform JSON row keys to database column names."""
    return {JSON_TO_DB_COLUMN.get(k, k): v for k, v in row.items()}


def insert_rows(cur, conn, schema: str, rows: list[dict]):
    """Insert video stats rows into the specified schema table."""
    if schema not in VALID_SCHEMAS:
        raise ValueError(f"Invalid schema: {schema}. Must be one of {VALID_SCHEMAS}")

    if schema == "staging":
        columns = (
            "video_id",
            "video_title",
            "published_at",
            "duration",
            "view_count",
            "like_count",
            "comment_count",
        )
    else:
        columns = (
            "video_id",
            "video_title",
            "published_at",
            "duration",
            "video_type",
            "view_count",
            "like_count",
            "comment_count",
        )

    try:
        for row in rows:
            transformed = _transform_row(row)
            placeholders = ", ".join(f"%({col})s" for col in columns)
            col_names = ", ".join(f'"{col}"' for col in columns)
            cur.execute(
                f"INSERT INTO {schema}.{TABLE} ({col_names}) VALUES ({placeholders})",
                transformed,
            )
        conn.commit()
        logger.info(f"Inserted {len(rows)} rows into {schema}.{TABLE}")
    except Exception as e:
        logger.error(f"Error inserting rows into {schema}.{TABLE}: {e}")
        conn.rollback()
        raise


def update_rows(cur, conn, schema: str, rows: list[dict]):
    """Update video stats rows in the specified schema table."""
    if schema not in VALID_SCHEMAS:
        raise ValueError(f"Invalid schema: {schema}. Must be one of {VALID_SCHEMAS}")

    if schema == "staging":
        columns = (
            "video_title",
            "published_at",
            "duration",
            "view_count",
            "like_count",
            "comment_count",
        )
    else:
        columns = (
            "video_title",
            "published_at",
            "duration",
            "video_type",
            "view_count",
            "like_count",
            "comment_count",
        )

    try:
        for row in rows:
            transformed = _transform_row(row)
            set_clause = ", ".join(f'"{col}" = %({col})s' for col in columns)
            cur.execute(
                f'UPDATE {schema}.{TABLE} SET {set_clause} WHERE "video_id" = %(video_id)s',
                transformed,
            )
        conn.commit()
        logger.info(f"Updated {len(rows)} rows in {schema}.{TABLE}")
    except Exception as e:
        logger.error(f"Error updating rows in {schema}.{TABLE}: {e}")
        conn.rollback()
        raise


def delete_rows(cur, conn, schema: str, rows: list[dict]):
    """Delete video stats rows from the specified schema table."""
    if schema not in VALID_SCHEMAS:
        raise ValueError(f"Invalid schema: {schema}. Must be one of {VALID_SCHEMAS}")

    try:
        ids_to_delete = ", ".join(f"'{row['video_id']}'" for row in rows)
        cur.execute(
            f'DELETE FROM {schema}.{TABLE} WHERE "video_id" IN ({ids_to_delete})'
        )
        conn.commit()
        logger.info(f"Deleted {len(rows)} rows from {schema}.{TABLE}")
    except Exception as e:
        logger.error(f"Error deleting rows from {schema}.{TABLE}: {e}")
        conn.rollback()
        raise
