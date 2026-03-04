import logging
from airflow.operators.bash import BashOperator

logger = logging.getLogger(__name__)

SODA_PATH = "/opt/airflow/include/soda"
DATASOURCE = "my_datasource"


def yt_elt_data_quality(schema):
    try:
        # Capture soda output and exit 0 if scan passes (telemetry errors return exit code 3)
        cmd = f"""
output=$(SODA_TELEMETRY=disabled OTEL_SDK_DISABLED=true soda scan -d {DATASOURCE} -c {SODA_PATH}/configuration.yml -v SCHEMA={schema} {SODA_PATH}/checks.yml 2>&1)
exit_code=$?
echo "$output"
if echo "$output" | grep -q "0 failures"; then
    exit 0
else
    exit $exit_code
fi
"""
        task = BashOperator(
            task_id=f"soda_test_{schema}",
            bash_command=cmd,
        )
        return task
    except Exception as e:
        logger.error(f"Error running data quality check for schema: {schema}")
        raise e
