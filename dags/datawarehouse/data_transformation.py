from datetime import timedelta, datetime


def parse_duration(duration):
    """Convert ISO 8601 duration (e.g., PT11H48M30S) to timedelta."""
    duration_str = duration.replace("P", "").replace("T", "")
    components = ("D", "H", "M", "S")  # Must be in order: days, hours, minutes, seconds
    values = {"D": 0, "H": 0, "M": 0, "S": 0}

    for component in components:
        if component in duration_str:
            value_str = duration_str.split(component)[0]
            values[component] = int(value_str)
            duration_str = duration_str.split(component)[1]

    total_duration = timedelta(
        days=values["D"], hours=values["H"], minutes=values["M"], seconds=values["S"]
    )

    return total_duration


def transform_data(row):
    duration_td = parse_duration(row["duration"])
    row["duration"] = (
        datetime.min + duration_td
    ).time()  # Convert timedelta to time format (HH:MM:SS)
    row["video_type"] = "short" if duration_td < timedelta(minutes=60) else "long"


if __name__ == "__main__":
    # Example usage
    video_duration = "PT23M4S"  # 1 hour, 2 minutes, and 3 seconds
    total_seconds = parse_duration(video_duration)
    print(total_seconds)
    test = (datetime.min + total_seconds).time()
    print(test)
