from django.core.cache import cache
import pandas as pd

DATA_KEY = "api:stored_data"
MULTI_KEY = "api:stored_multi_data"

def set_date_range_for_state(start_date, end_date):
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    multi = cache.get(MULTI_KEY)
    if multi:
        filtered = {}
        for s, df in multi.items():
            filtered[s] = df[(df.index >= start) & (df.index <= end)].copy()
        cache.set(MULTI_KEY, filtered, None)
        cache.set(DATA_KEY, None, None)  # indicate multi mode
        return

    single = cache.get(DATA_KEY)
    if single is not None:
        filtered = single[(single.index >= start) & (single.index <= end)].copy()
        cache.set(DATA_KEY, filtered, None)
