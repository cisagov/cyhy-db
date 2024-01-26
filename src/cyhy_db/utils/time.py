from datetime import datetime, timezone


def utcnow() -> datetime:
    """Returns a timezone-aware datetime object with the current time in UTC."""
    return datetime.now(timezone.utc)
