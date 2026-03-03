import json
from datetime import date
import logging

logger = logging.getLogger(__name__)


def load_path():

    file_path = f"../data/video_stats_{date.today()}.json"

    try:
        logger.info(f"Processing file: {file_path}")

        with open(file_path, "r", encoding="utf-8") as raw_data:
            data = json.load(raw_data)
            logger.info(f"Successfully loaded data from {file_path}")
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from file: {file_path}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading data: {e}")
        raise
