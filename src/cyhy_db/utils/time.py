# Standard Python Libraries
from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return a timezone-aware datetime object with the current time in UTC.

    This is useful for default value factories in Beanie models.

    Returns:
        datetime: The current time in UTC
    """
    return datetime.now(timezone.utc)
