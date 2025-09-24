import pandas as pd
import os
import yfinance as yf
from datetime import datetime, timedelta
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

def load_yfinance_data(tickers, start_date, end_date):
    """
    Load stock data from Yahoo Finance for multiple tickers.

    Parameters:
    - tickers: list of stock ticker symbols (e.g., ['AAPL', 'GOOGL', 'MSFT'])
    - start_date: start date string in 'YYYY-MM-DD' format
    - end_date: end date string in 'YYYY-MM-DD' format

    Returns:
    - dict with success message and loaded data info
    """
    if not tickers:
        raise ValueError("At least one ticker symbol is required")

    # Validate date format and convert to datetime
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD format")

    if start_dt >= end_dt:
        raise ValueError("Start date must be before end date")

    # Check if date range is reasonable (not too far in the past or future)
    today = datetime.now()
    if end_dt > today:
        end_dt = today
        end_date = end_dt.strftime('%Y-%m-%d')

    if start_dt < datetime(1970, 1, 1):
        raise ValueError("Start date cannot be before 1970-01-01")

    multi_data = {}
    failed_tickers = []

    for ticker in tickers:
        ticker = ticker.upper().strip()
        if not ticker:
            continue

        try:
            # Download data from yfinance
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date, auto_adjust=True, back_adjust=True)

            if df.empty:
                failed_tickers.append(ticker)
                continue

            # Standardize column names to match our expected format
            # yfinance returns: Open, High, Low, Close, Volume, Dividends, Stock Splits
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']

            # Check if we have the required columns
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                failed_tickers.append(ticker)
                continue

            # Keep only the required columns
            df = df[required_columns].copy()

            # Remove any rows with NaN values in OHLCV data
            df = df.dropna()

            if df.empty:
                failed_tickers.append(ticker)
                continue

            # Ensure the index is named 'Date' or convert it
            if df.index.name != 'Date':
                df.index.name = 'Date'

            multi_data[ticker] = df

        except Exception as e:
            print(f"Error loading data for {ticker}: {str(e)}")
            failed_tickers.append(ticker)

    if not multi_data:
        error_msg = "No valid data could be loaded for any ticker"
        if failed_tickers:
            error_msg += f". Failed tickers: {', '.join(failed_tickers)}"
        raise ValueError(error_msg)

    # Store in cache
    cache.set(MULTI_DATA_CACHE_KEY, multi_data, None)

    # Compute available date range from loaded data
    date_sets = [set(df.index) for df in multi_data.values()]
    common_dates = set.intersection(*date_sets)

    if not common_dates:
        # If no common dates, use the union of all dates
        all_dates = set.union(*date_sets)
        min_date, max_date = min(all_dates), max(all_dates)
        common_count = len(all_dates)
    else:
        min_date, max_date = min(common_dates), max(common_dates)
        common_count = len(common_dates)

    result = {
        'message': 'Data loaded successfully from Yahoo Finance',
        'stocks_loaded': list(multi_data.keys()),
        'failed_tickers': failed_tickers,
        'date_range': {
            'min_date': min_date.strftime('%Y-%m-%d'),
            'max_date': max_date.strftime('%Y-%m-%d')
        },
        'total_dates': common_count,
        'requested_date_range': {
            'start_date': start_date,
            'end_date': end_date
        }
    }

    if failed_tickers:
        result['warning'] = f"Failed to load data for: {', '.join(failed_tickers)}"

    return result
