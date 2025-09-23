import pandas as pd
import os
from django.core.cache import cache
# or from .state import set_stored_data, set_stored_multi_data

DATA_CACHE_KEY = "api:stored_data"
MULTI_DATA_CACHE_KEY = "api:stored_multi_data"

def upload_single_csv(file_obj):
    df = pd.read_csv(file_obj)
    required_columns = ['Open','High','Low','Close','Volume']
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns {missing}")

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

    # store in cache (or use database/state module)
    cache.set(DATA_CACHE_KEY, df, None)
    return len(df), list(df.columns)

def load_dow30_from_dir(data_dir):
    if not os.path.exists(data_dir):
        raise FileNotFoundError("Data directory not found")

    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    multi_data = {}
    for f in csv_files:
        path = os.path.join(data_dir, f)
        df = pd.read_csv(path)
        required_columns = ['Open','High','Low','Close','Volume']
        if any(c not in df.columns for c in required_columns):
            continue
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
        symbol = f.replace('_data.csv','').replace('.csv','')
        multi_data[symbol] = df

    if not multi_data:
        raise ValueError("No valid CSV files found")

    cache.set(MULTI_DATA_CACHE_KEY, multi_data, None)
    # compute available date range
    date_sets = [set(df.index) for df in multi_data.values()]
    common = set.intersection(*date_sets)
    min_date, max_date = min(common), max(common)
    return {
        'message': 'Loaded',
        'stocks_loaded': list(multi_data.keys()),
        'date_range': {'min_date': min_date.strftime('%Y-%m-%d'),
                       'max_date': max_date.strftime('%Y-%m-%d')},
        'total_dates': len(common)
    }
