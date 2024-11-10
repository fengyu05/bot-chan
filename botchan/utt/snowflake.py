import datetime


def extract_timestamp_from_snowflake(snowflake_id) -> int:
    twitter_epoch = 1288834974657
    # Bitwise operation to extract timestamp
    timestamp = ((snowflake_id >> 22) + twitter_epoch) / 1000.0

    return timestamp


def convert_slack_ts_to_datetime(ts):
    # Split the timestamp into its integer and fractional parts
    seconds_part, microseconds_part = ts.split(".")

    # Convert to datetime object by combining seconds and microseconds
    timestamp = datetime.datetime.utcfromtimestamp(
        int(seconds_part)
    ) + datetime.timedelta(microseconds=int(microseconds_part))

    return timestamp
