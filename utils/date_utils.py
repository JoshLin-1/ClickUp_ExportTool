from datetime import datetime, timedelta
from config import DATE_FORMAT, DEFAULT_TIME_PERIOD_DAYS


def get_default_date_range() -> tuple[str, str]:
    """Get default date range (last 7 days)"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=DEFAULT_TIME_PERIOD_DAYS)
    
    return (
        start_date.strftime(DATE_FORMAT),
        end_date.strftime(DATE_FORMAT)
    )


def parse_date_string(date_str: str) -> datetime:
    """Parse date string to datetime object"""
    return datetime.strptime(date_str, DATE_FORMAT)


def add_day_to_timestamp(date: datetime) -> datetime:
    """Add one day to datetime (for end date inclusivity)"""
    return date + timedelta(days=1)