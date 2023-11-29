from datetime import datetime, timedelta

def ceil_dt(dt, delta):
    return dt + (datetime.min - dt) % delta

def get_time_choices():
    now = datetime.now()
    asap = ceil_dt(now, timedelta(minutes=5))
    next_30_minutes = ceil_dt(now, timedelta(minutes=30))
    next_hour = ceil_dt(now, timedelta(hours=1))
    return (
        (asap, 'ASAP'),
        (next_30_minutes, 'Within the next 30 minutes'),
        (next_hour, 'Within the next hour'),
    )