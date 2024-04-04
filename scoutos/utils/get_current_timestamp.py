import datetime


def get_current_timestamp() -> str:
    """Return current timestamp in UTC as a string."""
    tz_utc = datetime.timezone.utc
    ts = datetime.datetime.now(tz=tz_utc)

    return ts.isoformat().replace("+00:00", "Z")
