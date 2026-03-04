from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import RealDictCursor

TABLE = "youtube_video_stats"


def get_conn_cursor() -> RealDictCursor:
    """Get a connection cursor to the Postgres database."""
    hook = PostgresHook(postgres_conn_id="postgres_db_yt_elt", database="elt_db")
    conn = hook.get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    return conn, cur


def close_conn_cursor(conn, cur) -> None:
    """Close the connection cursor."""
    cur.close()
    conn.close()


def create_schema(schema: str) -> None:
    """Create a new schema in the Postgres database."""
    conn, cur = get_conn_cursor()
    try:
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")
        conn.commit()
    except Exception as e:
        print(f"Error creating schema: {e}")
    finally:
        close_conn_cursor(conn, cur)


def create_table(schema: str, table: str) -> None:
    """Create a new table in the specified schema."""
    conn, cur = get_conn_cursor()
    if schema == "staging":
        table_sql = f"""
            CREATE TABLE IF NOT EXISTS {schema}.{table} (
                video_id VARCHAR(11) PRIMARY KEY NOT NULL,
                video_title TEXT NOT NULL,
                published_at TIMESTAMP NOT NULL,
                duration VARCHAR(20) NOT NULL ,
                view_count INT,
                like_count INT,
                comment_count INT
            );
        """
    elif schema == "core":
        table_sql = f"""
            CREATE TABLE IF NOT EXISTS {schema}.{table} (
                video_id VARCHAR(11) PRIMARY KEY NOT NULL,
                video_title TEXT NOT NULL,
                published_at TIMESTAMP NOT NULL,
                duration TIME NOT NULL,
                video_type VARCHAR(10) NOT NULL,
                view_count INT,
                like_count INT,
                comment_count INT
            );
        """
    cur.execute(table_sql)
    conn.commit()
    close_conn_cursor(conn, cur)
    print(f"Table {table} created successfully in schema {schema}.")


def get_video_ids_from_db(cur, schema: str) -> list[str]:
    """Fetch video IDs from the specified table."""

    cur.execute(f"SELECT video_id FROM {schema}.{TABLE};")
    rows = cur.fetchall()
    video_ids = [row["video_id"] for row in rows]
    return video_ids
