#!/usr/bin/env python3
"""
Script to download Dow Jones 30 historical data and save as CSV files.
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

# Current Dow Jones 30 companies (as of 2024)
DOW30_TICKERS = [
    'AAPL',  # Apple Inc.
    'MSFT',  # Microsoft Corp.
    'UNH',   # UnitedHealth Group
    'GS',    # Goldman Sachs
    'HD',    # Home Depot
    'CAT',   # Caterpillar
    'AMGN',  # Amgen
    'CRM',   # Salesforce
    'MCD',   # McDonald's
    'V',     # Visa
    'BA',    # Boeing
    'TRV',   # Travelers
    'AXP',   # American Express
    'JPM',   # JPMorgan Chase
    'IBM',   # IBM
    'HON',   # Honeywell
    'AAPL',  # Apple (duplicate removed below)
    'NKE',   # Nike
    'JNJ',   # Johnson & Johnson
    'MRK',   # Merck
    'PG',    # Procter & Gamble
    'CVX',   # Chevron
    'KO',    # Coca-Cola
    'DIS',   # Disney
    'MMM',   # 3M
    'INTC',  # Intel
    'VZ',    # Verizon
    'WMT',   # Walmart
    'CSCO',  # Cisco
    'DOW'    # Dow Inc.
]

# Remove duplicates and ensure we have exactly 30
DOW30_TICKERS = list(set(DOW30_TICKERS))[:30]

def download_dow30_data():
    """
    Download historical data for all Dow Jones 30 stocks.
    """
    data_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(data_dir, 'data')

    # Ensure data directory exists
    os.makedirs(data_folder, exist_ok=True)

    # Date range: Last 5 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)

    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    print(f"Downloading Dow Jones 30 data from {start_str} to {end_str}")
    print(f"Data will be saved to: {data_folder}")
    print("-" * 60)

    successful_downloads = 0
    failed_downloads = []

    for ticker in DOW30_TICKERS:
        try:
            print(f"Downloading {ticker}...", end=' ')

            # Download data
            stock = yf.Ticker(ticker)
            df = stock.history(
                start=start_str,
                end=end_str,
                auto_adjust=True,
                back_adjust=True
            )

            if df.empty:
                print("❌ No data available")
                failed_downloads.append(ticker)
                continue

            # Keep only OHLCV columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df = df[required_columns].copy()

            # Remove rows with NaN values
            df = df.dropna()

            if df.empty:
                print("❌ No valid data after cleaning")
                failed_downloads.append(ticker)
                continue

            # Reset index to make Date a column
            df.reset_index(inplace=True)

            # Ensure Date column is properly formatted
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

            # Reorder columns: Date first, then OHLCV
            df = df[['Date'] + required_columns]

            # Save to CSV
            filename = f"{ticker}_data.csv"
            filepath = os.path.join(data_folder, filename)
            df.to_csv(filepath, index=False)

            print(f"✅ {len(df)} rows saved")
            successful_downloads += 1

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            failed_downloads.append(ticker)

    print("-" * 60)
    print(f"Download completed!")
    print(f"✅ Successful: {successful_downloads} stocks")
    print(f"❌ Failed: {len(failed_downloads)} stocks")

    if failed_downloads:
        print(f"Failed tickers: {', '.join(failed_downloads)}")

    # Create a summary file
    summary_file = os.path.join(data_folder, 'download_summary.txt')
    with open(summary_file, 'w') as f:
        f.write(f"Dow Jones 30 Data Download Summary\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Date range: {start_str} to {end_str}\n")
        f.write(f"Successful downloads: {successful_downloads}\n")
        f.write(f"Failed downloads: {len(failed_downloads)}\n")
        f.write(f"\nSuccessful tickers:\n")
        for ticker in DOW30_TICKERS:
            if ticker not in failed_downloads:
                f.write(f"  {ticker}\n")
        if failed_downloads:
            f.write(f"\nFailed tickers:\n")
            for ticker in failed_downloads:
                f.write(f"  {ticker}\n")

    print(f"Summary saved to: {summary_file}")

if __name__ == '__main__':
    download_dow30_data()