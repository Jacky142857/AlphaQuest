#!/usr/bin/env python3
"""
Equal-Weighted Dow Jones 30 Portfolio Calculator
Calculates performance from 2019/03/20 to 2024/12/31
"""

import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime
import matplotlib.pyplot as plt

def load_dj30_data(data_dir='data'):
    """Load all DJ30 stock data from CSV files"""
    print("Loading Dow Jones 30 data...")
    print(f"Looking in directory: {os.path.abspath(data_dir)}")

    if not os.path.exists(data_dir):
        print(f"Error: Data directory '{data_dir}' not found!")
        print(f"Current working directory: {os.getcwd()}")
        print("Available files:")
        try:
            print(os.listdir('.'))
        except:
            pass
        return None

    # Find all CSV files
    csv_files = glob.glob(os.path.join(data_dir, '*.csv'))

    if not csv_files:
        print(f"Error: No CSV files found in '{data_dir}'!")
        return None

    stock_data = {}

    for csv_file in csv_files:
        # Extract stock symbol from filename
        stock_symbol = os.path.basename(csv_file).replace('_data.csv', '').replace('.csv', '')

        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            print(f"  Reading {stock_symbol}: {len(df)} rows, columns: {list(df.columns)}")

            # Validate required columns
            required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                print(f"  Warning: Skipping {stock_symbol} - missing columns: {missing_columns}")
                continue

            # Filter to only required columns (plus Date)
            df = df[required_columns].copy()

            # Convert Date column to datetime and set as index
            try:
                # Use utc=True to handle mixed timezones properly
                df['Date'] = pd.to_datetime(df['Date'], utc=True)

                # Convert to timezone-naive for consistency
                if hasattr(df['Date'], 'dt') and df['Date'].dt.tz is not None:
                    df['Date'] = df['Date'].dt.tz_localize(None)
            except Exception as date_error:
                print(f"  Error parsing dates for {stock_symbol}: {date_error}")
                # Try alternative date parsing
                try:
                    df['Date'] = pd.to_datetime(df['Date'], infer_datetime_format=True)
                    if hasattr(df['Date'], 'dt') and df['Date'].dt.tz is not None:
                        df['Date'] = df['Date'].dt.tz_localize(None)
                except:
                    print(f"  Failed to parse dates for {stock_symbol}, skipping")
                    continue

            df.set_index('Date', inplace=True)

            # Sort by date and remove any duplicates
            df = df.sort_index()
            df = df[~df.index.duplicated(keep='first')]

            # Ensure numeric columns are float
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Remove rows with NaN values
            df = df.dropna()

            if len(df) > 0:
                stock_data[stock_symbol] = df
                print(f"  Successfully loaded {stock_symbol}: {len(df)} rows from {df.index.min()} to {df.index.max()}")
            else:
                print(f"  Warning: {stock_symbol} has no valid data after cleaning")

        except Exception as e:
            print(f"  Error loading {stock_symbol}: {str(e)}")
            import traceback
            print(f"  Traceback: {traceback.format_exc()}")
            continue

    print(f"Successfully loaded {len(stock_data)} stocks")
    return stock_data

def filter_date_range(stock_data, start_date, end_date):
    """Filter stock data to specified date range and find intersection"""
    print(f"\nFiltering data from {start_date} to {end_date}...")

    # Ensure start and end dates are timezone-naive
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if start_date.tz is not None:
        start_date = start_date.tz_localize(None)
    if end_date.tz is not None:
        end_date = end_date.tz_localize(None)

    print(f"Target date range: {start_date} to {end_date}")
    print(f"Processing {len(stock_data)} stocks for date filtering...")

    # Find date intersection across all stocks
    common_dates = None
    for symbol, df in stock_data.items():
        try:
            # Ensure DataFrame index is timezone-naive
            if hasattr(df.index, 'tz') and df.index.tz is not None:
                df.index = df.index.tz_localize(None)
                stock_data[symbol] = df  # Update the original data

            # Filter to date range first
            mask = (df.index >= start_date) & (df.index <= end_date)
            filtered_dates = set(df.index[mask])

            print(f"  {symbol}: {len(filtered_dates)} dates in range")

            if common_dates is None:
                common_dates = filtered_dates
            else:
                common_dates = common_dates.intersection(filtered_dates)

        except Exception as e:
            print(f"  Error processing {symbol}: {str(e)}")
            import traceback
            print(f"  Traceback: {traceback.format_exc()}")
            continue

    if not common_dates:
        print("Error: No common dates found across stocks!")
        return None, None

    common_dates = sorted(list(common_dates))
    print(f"Found {len(common_dates)} common trading dates")
    print(f"Date range: {common_dates[0].strftime('%Y-%m-%d')} to {common_dates[-1].strftime('%Y-%m-%d')}")

    # Filter all stocks to common dates
    filtered_data = {}
    for symbol, df in stock_data.items():
        filtered_df = df.loc[df.index.isin(common_dates)].sort_index()
        if len(filtered_df) > 0:
            filtered_data[symbol] = filtered_df

    return filtered_data, common_dates

def calculate_equal_weighted_portfolio(stock_data, common_dates):
    """Calculate equal-weighted portfolio performance"""
    print("\nCalculating equal-weighted portfolio...")

    # Create price DataFrame
    symbols = list(stock_data.keys())
    close_prices = pd.DataFrame(index=common_dates, columns=symbols)

    for symbol in symbols:
        close_prices[symbol] = stock_data[symbol]['Close']

    # Calculate daily returns
    daily_returns = close_prices.pct_change().dropna()

    # Equal weighted portfolio return (average of all stock returns)
    portfolio_returns = daily_returns.mean(axis=1)

    # Calculate cumulative returns
    cumulative_returns = (1 + portfolio_returns).cumprod()

    # Calculate performance metrics
    total_return = cumulative_returns.iloc[-1] - 1
    annualized_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1
    volatility = portfolio_returns.std() * np.sqrt(252)
    sharpe_ratio = annualized_return / volatility if volatility > 0 else 0

    # Maximum drawdown
    running_max = cumulative_returns.expanding(min_periods=1).max()
    drawdown = (cumulative_returns - running_max) / running_max
    max_drawdown = drawdown.min()

    return {
        'portfolio_returns': portfolio_returns,
        'cumulative_returns': cumulative_returns,
        'daily_returns_df': daily_returns,
        'close_prices': close_prices,
        'metrics': {
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'annualized_return': annualized_return,
            'annualized_return_pct': annualized_return * 100,
            'volatility': volatility,
            'volatility_pct': volatility * 100,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'num_stocks': len(symbols),
            'num_trading_days': len(portfolio_returns)
        }
    }

def print_results(results, symbols, start_date, end_date):
    """Print portfolio performance results"""
    metrics = results['metrics']

    print("="*60)
    print("EQUAL-WEIGHTED DOW JONES 30 PORTFOLIO PERFORMANCE")
    print("="*60)
    print(f"Period: {start_date} to {end_date}")
    print(f"Number of Stocks: {metrics['num_stocks']}")
    print(f"Trading Days: {metrics['num_trading_days']}")
    print(f"Stock Symbols: {', '.join(sorted(symbols))}")
    print()

    print("PERFORMANCE METRICS:")
    print("-" * 30)
    print(f"Total Return:      {metrics['total_return_pct']:+8.2f}%")
    print(f"Annualized Return: {metrics['annualized_return_pct']:+8.2f}%")
    print(f"Volatility:        {metrics['volatility_pct']:8.2f}%")
    print(f"Sharpe Ratio:      {metrics['sharpe_ratio']:8.2f}")
    print(f"Max Drawdown:      {metrics['max_drawdown_pct']:8.2f}%")
    print()

    # Show best and worst days
    portfolio_returns = results['portfolio_returns']
    best_day = portfolio_returns.max()
    worst_day = portfolio_returns.min()
    best_date = portfolio_returns.idxmax()
    worst_date = portfolio_returns.idxmin()

    print("EXTREME DAYS:")
    print("-" * 30)
    print(f"Best Day:  {best_day:+8.2%} on {best_date.strftime('%Y-%m-%d')}")
    print(f"Worst Day: {worst_day:+8.2%} on {worst_date.strftime('%Y-%m-%d')}")
    print()

def plot_performance(results, start_date, end_date, save_plot=True):
    """Plot cumulative performance"""
    try:
        import matplotlib.pyplot as plt

        cumulative_returns = results['cumulative_returns']

        plt.figure(figsize=(12, 8))

        # Main performance plot
        plt.subplot(2, 1, 1)
        plt.plot(cumulative_returns.index, (cumulative_returns - 1) * 100,
                 linewidth=2, color='#2E86AB', label='Equal-Weighted DJ30')
        plt.title('Equal-Weighted Dow Jones 30 Portfolio Performance', fontsize=16, fontweight='bold')
        plt.ylabel('Cumulative Return (%)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()

        # Drawdown plot
        plt.subplot(2, 1, 2)
        running_max = cumulative_returns.expanding(min_periods=1).max()
        drawdown = (cumulative_returns - running_max) / running_max * 100
        plt.fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.3)
        plt.plot(drawdown.index, drawdown, color='red', linewidth=1)
        plt.title('Drawdown (%)', fontsize=14)
        plt.ylabel('Drawdown (%)', fontsize=12)
        plt.xlabel('Date', fontsize=12)
        plt.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_plot:
            plt.savefig('equal_weighted_dj30_performance.png', dpi=300, bbox_inches='tight')
            print("Performance chart saved as 'equal_weighted_dj30_performance.png'")

        plt.show()

    except ImportError:
        print("Matplotlib not available - skipping chart generation")

def save_results_to_csv(results, filename='equal_weighted_dj30_results.csv'):
    """Save detailed results to CSV"""
    portfolio_data = pd.DataFrame({
        'Date': results['cumulative_returns'].index,
        'Daily_Return': results['portfolio_returns'].values,
        'Cumulative_Return': results['cumulative_returns'].values - 1,
        'Portfolio_Value': results['cumulative_returns'].values * 10000  # Assuming $10,000 initial investment
    })

    portfolio_data.to_csv(filename, index=False)
    print(f"Detailed results saved to '{filename}'")

def main():
    # Configuration
    START_DATE = '2019-03-20'
    END_DATE = '2024-12-31'
    DATA_DIR = 'data'

    print("Equal-Weighted Dow Jones 30 Portfolio Calculator")
    print("=" * 50)

    # Load data
    stock_data = load_dj30_data(DATA_DIR)
    if stock_data is None:
        return

    # Filter to date range
    filtered_data, common_dates = filter_date_range(stock_data, START_DATE, END_DATE)
    if filtered_data is None or common_dates is None:
        print("Failed to filter data to date range. Exiting.")
        return

    # Calculate portfolio performance
    results = calculate_equal_weighted_portfolio(filtered_data, common_dates)

    # Print results
    symbols = list(filtered_data.keys())
    print_results(results, symbols, START_DATE, END_DATE)

    # Save results
    save_results_to_csv(results)

    # Plot results
    plot_performance(results, START_DATE, END_DATE)

    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()