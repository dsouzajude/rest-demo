import uuid
from datetime import datetime


def format_datetime(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def to_datetime(date_str):
    """ Returns a datetime python object for a date: yyyy-mm-dd
    or datetime: 'yyyy-mm-ddTHH:MM:SS' or 'yyyy-mm-dd HH:MM:SS' representation
    """
    if 'T' in date_str:
        return datetime.strptime(date_str.strip(), "%Y-%m-%dT%H:%M:%SZ")
    elif ' ' in date_str:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M:%S")
    else:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d")


def generate_uuid():
    return str(uuid.uuid4())
