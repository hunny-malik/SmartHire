from datetime import datetime, timezone

def utc_now() -> datetime:
    """Return naive UTC datetime safe for SQLite and PostgreSQL without deprecation warnings."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
