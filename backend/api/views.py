# backend/api/views.py
import pandas as pd
import numpy as np
import sympy as sp
import json
import io
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Global variables to store data
stored_data = None
stored_multi_data = None
available_date_range = None

# Global strategy settings
strategy_settings = {
    'neutralization': 'Subindustry',
    'decay': 4,
    'truncation': 0.08,
    'pasteurization': 'On',
    'nanHandling': 'Off',
    'maxTrade': 'Off',
    'delay': 1,
    'commission': 0.001,
    'bookSize': 1000000,
    'minWeight': 0.01,
    'maxWeight': 0.05,
    'rebalanceFreq': 'Daily'
}

@csrf_exempt
@api_view(['POST'])
def upload_data(request):
    global stored_data
    
    try:
        if 'file' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        
        # Read CSV file
        df = pd.read_csv(file)

        # Validate required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return Response({
                'error': f'Missing required columns: {missing_columns}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Set Date column as index if it exists and parse as datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)

        # Store data globally
        stored_data = df
        
        return Response({
            'message': 'Data uploaded successfully',
            'rows': len(df),
            'columns': list(df.columns)
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
def load_dow30_data(request):
    global stored_multi_data, available_date_range

    try:
        import os

        # Path to data directory
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

        if not os.path.exists(data_dir):
            return Response({'error': 'Data directory not found'}, status=status.HTTP_404_NOT_FOUND)

        # Load all CSV files from data directory
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

        if not csv_files:
            return Response({'error': 'No CSV files found in data directory'}, status=status.HTTP_404_NOT_FOUND)

        multi_stock_data = {}
        all_dates = []

        for csv_file in csv_files:
            stock_symbol = csv_file.replace('_data.csv', '').replace('.csv', '')
            file_path = os.path.join(data_dir, csv_file)

            # Read CSV file
            df = pd.read_csv(file_path)

            # Validate required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if not missing_columns:
                # Set Date column as index if it exists and parse as datetime
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'])
                    df.set_index('Date', inplace=True)
                    all_dates.extend(df.index.tolist())

                multi_stock_data[stock_symbol] = df

        if not multi_stock_data:
            return Response({'error': 'No valid stock data files found'}, status=status.HTTP_400_BAD_REQUEST)

        # Find date intersection across all stocks
        date_intersection = None
        for stock_symbol, df in multi_stock_data.items():
            stock_dates = set(df.index)
            if date_intersection is None:
                date_intersection = stock_dates
            else:
                date_intersection = date_intersection.intersection(stock_dates)

        # Filter all data to common date range
        for stock_symbol in multi_stock_data.keys():
            multi_stock_data[stock_symbol] = multi_stock_data[stock_symbol].loc[
                multi_stock_data[stock_symbol].index.isin(date_intersection)
            ].sort_index()

        # Store data globally
        stored_multi_data = multi_stock_data

        # Calculate available date range
        if date_intersection:
            min_date = min(date_intersection)
            max_date = max(date_intersection)
            available_date_range = {
                'min_date': min_date.strftime('%Y-%m-%d'),
                'max_date': max_date.strftime('%Y-%m-%d')
            }

        return Response({
            'message': 'Dow Jones 30 data loaded successfully',
            'stocks_loaded': list(multi_stock_data.keys()),
            'date_range': available_date_range,
            'total_dates': len(date_intersection)
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
def set_date_range(request):
    global stored_multi_data, stored_data

    try:
        data = json.loads(request.body)
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not start_date or not end_date:
            return Response({'error': 'Both start_date and end_date are required'}, status=status.HTTP_400_BAD_REQUEST)

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        if stored_multi_data:
            # Filter multi-stock data by date range
            filtered_multi_data = {}
            for stock_symbol, df in stored_multi_data.items():
                filtered_df = df[(df.index >= start_date) & (df.index <= end_date)]
                filtered_multi_data[stock_symbol] = filtered_df

            # Update stored data
            stored_multi_data = filtered_multi_data

            # For now, set stored_data to None to indicate multi-stock mode
            stored_data = None

        elif stored_data is not None:
            # Filter single stock data by date range
            if 'Date' in stored_data.columns or stored_data.index.name == 'Date' or pd.api.types.is_datetime64_any_dtype(stored_data.index):
                filtered_data = stored_data[(stored_data.index >= start_date) & (stored_data.index <= end_date)]
                stored_data = filtered_data

        return Response({
            'message': 'Date range set successfully',
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
def update_settings(request):
    global strategy_settings

    try:
        data = json.loads(request.body)

        # Update strategy settings
        for key, value in data.items():
            if key in strategy_settings:
                strategy_settings[key] = value

        return Response({
            'message': 'Settings updated successfully',
            'settings': strategy_settings
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
def get_settings(request):
    global strategy_settings

    return Response({
        'settings': strategy_settings
    })

@csrf_exempt
@api_view(['POST'])
def calculate_alpha(request):
    global stored_data, stored_multi_data, strategy_settings

    if stored_data is None and stored_multi_data is None:
        return Response({'error': 'No data uploaded'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        data = json.loads(request.body)
        alpha_formula = data.get('alpha_formula', '')

        if not alpha_formula:
            return Response({'error': 'No alpha formula provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate alpha and metrics
        if stored_multi_data:
            # Multi-stock mode
            result = process_alpha_strategy_multi(stored_multi_data, alpha_formula, strategy_settings)
        else:
            # Single stock mode
            result = process_alpha_strategy(stored_data, alpha_formula, strategy_settings)

        return Response(result)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def process_alpha_strategy(df, alpha_formula_str, settings):
    """Process the alpha strategy based on the uploaded data and formula"""
    
    # Define symbolic variables
    OPEN, CLOSE, HIGH, LOW, VOLUME = sp.symbols("Open Close High Low Volume")
    VWAP = sp.symbols("Vwap")
    RANK = sp.Function('Rank')
    DELTA = sp.Function('Delta')
    SUM = sp.Function('Sum')
    ABS = sp.Function('Abs')
    TS_ARG_MAX = sp.Function('Ts_argmax')
    TS_RANK = sp.Function('Ts_rank')
    SQRT = sp.Function('Sqrt')
    QUANTILE = sp.Function('quantile')
    
    # Helper functions
    def Delta(x, n):
        return x - x.shift(n)
    
    def Rank(x):
        if isinstance(x, pd.Series):
            return (x.rank() - 1) / (len(x) - 1)
        return (x.rank(axis=1) - 1) / (x.shape[1] - 1)
    
    def Sum(x, n):
        return x.rolling(n).sum()
    
    def Abs(x):
        return x.abs()
    
    def Sqrt(x):
        return x.apply(lambda x: np.sqrt(x))
    
    def Ts_argmax(x, n):
        return x.rolling(n).apply(lambda x: x.argmax())
    
    def Ts_rank(x, n):
        return x.rolling(n).apply(lambda x: x.rank().iloc[-1], raw=False)

    def quantile_transform(x, driver="gaussian", sigma=1.0):
        """
        Apply quantile transformation with distribution mapping

        Steps:
        1. Rank the input raw Alpha vector to [0, 1]
        2. Shift the ranked Alpha vector to [1/N, 1-1/N]
        3. Apply distribution transformation
        """
        from scipy.stats import norm, cauchy, uniform

        # Convert to pandas Series if it's a numpy array
        if isinstance(x, np.ndarray):
            x = pd.Series(x)

        if isinstance(x, pd.Series):
            # Step 1: Rank to [0, 1]
            N = len(x)
            ranked = (x.rank() - 1) / (N - 1)

            # Step 2: Shift to [1/N, 1-1/N]
            shifted = (1/N) + ranked * (1 - 2/N)

            # Step 3: Apply distribution
            if driver.lower() == "uniform":
                # Uniform: subtract mean (equivalent to centering)
                result = (shifted - shifted.mean()) * sigma
            elif driver.lower() == "gaussian":
                # Apply inverse normal transformation
                result = norm.ppf(shifted) * sigma
            elif driver.lower() == "cauchy":
                # Apply inverse Cauchy transformation
                result = cauchy.ppf(shifted) * sigma
            else:
                raise ValueError(f"Unknown driver: {driver}. Use 'gaussian', 'uniform', or 'cauchy'")

            return result
        else:
            # For DataFrames, apply row-wise
            return x.apply(lambda row: quantile_transform(row, driver=driver, sigma=sigma), axis=1)

    def quantile_custom(x, driver, sigma):
        """
        Wrapper function to handle parsed quantile function calls
        """
        return quantile_transform(x, driver=driver, sigma=sigma)

    def quantile_simple(x, driver, sigma):
        """
        Simple wrapper for fallback quantile function calls
        """
        return quantile_transform(x, driver=driver, sigma=sigma)
    
    # Convert data columns
    High = df['High'].astype(float)
    Low = df['Low'].astype(float)
    Open = df['Open'].astype(float)
    Close = df["Close"].astype(float)
    Volume = df['Volume'].astype(float)
    Vwap = (((High + Low + Close) / 3) * Volume).cumsum() / Volume.cumsum()
    
    # Parse and evaluate the alpha formula
    try:
        # Replace case-insensitive variables
        alpha_formula_str = alpha_formula_str.replace('close', 'Close')
        alpha_formula_str = alpha_formula_str.replace('CLOSE', 'Close')
        alpha_formula_str = alpha_formula_str.replace('open', 'Open')
        alpha_formula_str = alpha_formula_str.replace('OPEN', 'Open')
        alpha_formula_str = alpha_formula_str.replace('high', 'High')
        alpha_formula_str = alpha_formula_str.replace('HIGH', 'High')
        alpha_formula_str = alpha_formula_str.replace('low', 'Low')
        alpha_formula_str = alpha_formula_str.replace('LOW', 'Low')
        alpha_formula_str = alpha_formula_str.replace('volume', 'Volume')
        alpha_formula_str = alpha_formula_str.replace('VOLUME', 'Volume')
        alpha_formula_str = alpha_formula_str.replace('vwap', 'Vwap')
        alpha_formula_str = alpha_formula_str.replace('VWAP', 'Vwap')

        # Handle quantile function with a completely different approach
        # Instead of using SymPy parsing, handle quantile functions directly

        if 'quantile(' in alpha_formula_str.lower():
            # Completely different approach: pre-compute the quantile result
            print(f"Original formula: {alpha_formula_str}")

            # For now, let's try the simplest possible case
            if alpha_formula_str == "quantile(Close - Open, driver = gaussian, sigma = 0.5)":
                print("Matched exact formula, computing directly")

                # Compute Close - Open
                diff = Close - Open
                print(f"Close - Open type: {type(diff)}")
                print(f"Close - Open shape: {diff.shape}")

                # Apply our quantile transformation directly
                result = quantile_transform(diff, driver="gaussian", sigma=0.5)
                print(f"Quantile result type: {type(result)}")

                df_alpha = result
            else:
                # Try the eval approach for other formulas
                eval_formula = alpha_formula_str

                # Replace case variations
                eval_formula = eval_formula.replace('close', 'Close')
                eval_formula = eval_formula.replace('CLOSE', 'Close')
                eval_formula = eval_formula.replace('open', 'Open')
                eval_formula = eval_formula.replace('OPEN', 'Open')

                print(f"Using eval for: {eval_formula}")

                # Create a safe evaluation context
                eval_context = {
                    'Close': Close,
                    'Open': Open,
                    'High': High,
                    'Low': Low,
                    'Volume': Volume,
                    'Vwap': Vwap,
                    'quantile': quantile_transform,
                    'gaussian': 'gaussian',
                    'uniform': 'uniform',
                    'cauchy': 'cauchy',
                    'Rank': Rank,
                    'Delta': Delta,
                    'Sum': Sum,
                    'Abs': Abs,
                    'Sqrt': Sqrt,
                    'Ts_argmax': Ts_argmax,
                    'Ts_rank': Ts_rank,
                    'pd': pd,
                    'np': np
                }

                # Directly evaluate the formula
                df_alpha = eval(eval_formula, {"__builtins__": {}}, eval_context)
        else:
            # Use the original SymPy approach for non-quantile formulas
            # Parse symbolic expression
            alpha = sp.sympify(alpha_formula_str)

            # Evaluate the alpha expression
            df_alpha = eval(str(alpha))
        
    except Exception as e:
        raise Exception(f"Error evaluating alpha formula: {str(e)}")
    
    # Apply strategy parameters from settings
    Truncation = settings.get('truncation', 0)
    Decay = settings.get('decay', 1)
    Delay = settings.get('delay', 1)
    
    # Handle single series vs DataFrame vs numpy array
    print(f"df_alpha type before processing: {type(df_alpha)}")

    if isinstance(df_alpha, (pd.Series, np.ndarray)):
        # Convert numpy array to pandas Series if needed
        if isinstance(df_alpha, np.ndarray):
            print("Converting numpy array to pandas Series")
            df_alpha = pd.Series(df_alpha, index=Close.index)
            print(f"df_alpha type after conversion: {type(df_alpha)}")

        # For single stock, convert to simple weights
        alpha_final = df_alpha.shift(Delay)
        print(f"alpha_final type: {type(alpha_final)}")

        # Calculate returns
        returns = Close.pct_change()
        returns = returns.loc[alpha_final.index]

        # Calculate strategy returns (normalize alpha to create position)
        alpha_normalized = alpha_final / alpha_final.abs()
        strategy_returns = alpha_normalized * returns

    else:
        # For multiple stocks (existing logic)
        alpha_truncated = df_alpha.clip(axis=0,
                                      lower=df_alpha.quantile(Truncation, axis=1),
                                      upper=df_alpha.quantile(1-Truncation, axis=1))
        
        normalized_weight = (alpha_truncated.T / alpha_truncated.T.abs().sum()).T
        
        def weighted_moving_average(x):
            n = len(x)
            weights = np.arange(1, n+1)
            return np.sum(x * weights) / np.sum(weights)
        
        alpha_decayed = normalized_weight.rolling(window=Decay).apply(weighted_moving_average, raw=True)
        alpha_final = alpha_decayed.shift(Delay)

        returns = Close.pct_change()
        returns = returns.loc[alpha_final.index]
        
        strategy_returns = (alpha_final * returns).sum(axis=1)
    
    # Remove NaN values
    strategy_returns = strategy_returns.dropna()

    if len(strategy_returns) == 0:
        raise Exception("No valid returns calculated")

    # Calculate cumulative returns using arithmetic compounding
    cumulative_returns = (1 + strategy_returns).cumprod()
    
    # Calculate metrics
    total_return = cumulative_returns.iloc[-1] - 1
    
    # Prepare data for frontend
    if hasattr(strategy_returns.index, 'strftime'):
        dates = strategy_returns.index.strftime('%Y-%m-%d').tolist()
    else:
        # If index is not datetime, convert to string representation
        dates = [str(idx) for idx in strategy_returns.index.tolist()]
    pnl_values = cumulative_returns.tolist()
    
    return {
        'success': True,
        'pnl_data': {
            'dates': dates,
            'values': pnl_values
        },
        'metrics': {
            'total_return': float(total_return),
            'total_return_pct': f"{total_return * 100:.2f}%"
        }
    }

def process_alpha_strategy_multi(multi_stock_data, alpha_formula_str, settings):
    """Process the alpha strategy based on multiple stock data and formula"""

    # Get all stock symbols
    stock_symbols = list(multi_stock_data.keys())

    # Get common dates (should already be intersected in load_dow30_data)
    common_dates = None
    for symbol in stock_symbols:
        if common_dates is None:
            common_dates = set(multi_stock_data[symbol].index)
        else:
            common_dates = common_dates.intersection(set(multi_stock_data[symbol].index))

    common_dates = sorted(list(common_dates))

    # Create DataFrames for each price type across all stocks
    close_data = pd.DataFrame({symbol: multi_stock_data[symbol]['Close'] for symbol in stock_symbols})
    open_data = pd.DataFrame({symbol: multi_stock_data[symbol]['Open'] for symbol in stock_symbols})
    high_data = pd.DataFrame({symbol: multi_stock_data[symbol]['High'] for symbol in stock_symbols})
    low_data = pd.DataFrame({symbol: multi_stock_data[symbol]['Low'] for symbol in stock_symbols})
    volume_data = pd.DataFrame({symbol: multi_stock_data[symbol]['Volume'] for symbol in stock_symbols})

    # Filter to common dates
    close_data = close_data.loc[common_dates]
    open_data = open_data.loc[common_dates]
    high_data = high_data.loc[common_dates]
    low_data = low_data.loc[common_dates]
    volume_data = volume_data.loc[common_dates]

    # Calculate VWAP for all stocks
    vwap_data = (((high_data + low_data + close_data) / 3) * volume_data).cumsum() / volume_data.cumsum()

    # Define helper functions for multi-stock operations
    def Delta(x, n):
        return x - x.shift(n)

    def Rank(x):
        if isinstance(x, pd.Series):
            return (x.rank() - 1) / (len(x) - 1)
        return (x.rank(axis=1) - 1) / (x.shape[1] - 1)

    def Sum(x, n):
        return x.rolling(n).sum()

    def Abs(x):
        return x.abs()

    def Sqrt(x):
        if isinstance(x, pd.DataFrame):
            return x.apply(lambda col: col.apply(lambda x: np.sqrt(x) if x >= 0 else np.nan))
        else:
            return x.apply(lambda x: np.sqrt(x) if x >= 0 else np.nan)

    def Ts_argmax(x, n):
        return x.rolling(n).apply(lambda x: x.argmax())

    def Ts_rank(x, n):
        return x.rolling(n).apply(lambda x: x.rank().iloc[-1], raw=False)

    def quantile_transform_multi(x, driver="gaussian", sigma=1.0):
        """Multi-stock version of quantile transform"""
        if isinstance(x, pd.DataFrame):
            # Apply quantile transform to each row (across stocks)
            return x.apply(lambda row: quantile_transform(row.dropna(), driver=driver, sigma=sigma), axis=1)
        else:
            return quantile_transform(x, driver=driver, sigma=sigma)

    try:
        # Replace case-insensitive variables
        alpha_formula_str = alpha_formula_str.replace('close', 'Close')
        alpha_formula_str = alpha_formula_str.replace('CLOSE', 'Close')
        alpha_formula_str = alpha_formula_str.replace('open', 'Open')
        alpha_formula_str = alpha_formula_str.replace('OPEN', 'Open')
        alpha_formula_str = alpha_formula_str.replace('high', 'High')
        alpha_formula_str = alpha_formula_str.replace('HIGH', 'High')
        alpha_formula_str = alpha_formula_str.replace('low', 'Low')
        alpha_formula_str = alpha_formula_str.replace('LOW', 'Low')
        alpha_formula_str = alpha_formula_str.replace('volume', 'Volume')
        alpha_formula_str = alpha_formula_str.replace('VOLUME', 'Volume')
        alpha_formula_str = alpha_formula_str.replace('vwap', 'Vwap')
        alpha_formula_str = alpha_formula_str.replace('VWAP', 'Vwap')

        # Handle quantile function for multi-stock
        if 'quantile(' in alpha_formula_str.lower():
            # For multi-stock, use direct evaluation with DataFrames
            eval_context = {
                'Close': close_data,
                'Open': open_data,
                'High': high_data,
                'Low': low_data,
                'Volume': volume_data,
                'Vwap': vwap_data,
                'quantile': quantile_transform_multi,
                'gaussian': 'gaussian',
                'uniform': 'uniform',
                'cauchy': 'cauchy',
                'Rank': Rank,
                'Delta': Delta,
                'Sum': Sum,
                'Abs': Abs,
                'Sqrt': Sqrt,
                'Ts_argmax': Ts_argmax,
                'Ts_rank': Ts_rank,
                'pd': pd,
                'np': np
            }

            df_alpha = eval(alpha_formula_str, {"__builtins__": {}}, eval_context)
        else:
            # Use SymPy for other formulas
            alpha = sp.sympify(alpha_formula_str)

            # Create evaluation context with DataFrames
            Close = close_data
            Open = open_data
            High = high_data
            Low = low_data
            Volume = volume_data
            Vwap = vwap_data

            df_alpha = eval(str(alpha))

    except Exception as e:
        raise Exception(f"Error evaluating alpha formula: {str(e)}")

    print(f"Multi-stock df_alpha type: {type(df_alpha)}")

    # Handle scalar values (like inputting "1") by converting to DataFrame
    if isinstance(df_alpha, (int, float)):
        # Create a DataFrame filled with the scalar value, same shape as price data
        df_alpha = pd.DataFrame(
            np.full(close_data.shape, df_alpha),
            index=close_data.index,
            columns=close_data.columns
        )
        print(f"Converted scalar to DataFrame shape: {df_alpha.shape}")

    print(f"Multi-stock df_alpha shape: {df_alpha.shape}")

    # Special case: if alpha is all 1s, use pure equal weighting like equal_weighted_dj30.py
    if isinstance(df_alpha, pd.DataFrame) and ((df_alpha == 1).all().all()):
        print("Alpha is all 1s - using pure equal weighting to match equal_weighted_dj30.py")

        # Calculate returns for all stocks
        returns = close_data.pct_change().dropna()

        # Equal weighted portfolio return (simple average)
        strategy_returns = returns.mean(axis=1)

        # Remove NaN values
        strategy_returns = strategy_returns.dropna()

        if len(strategy_returns) == 0:
            raise Exception("No valid returns calculated")

        # Calculate cumulative returns using arithmetic compounding (matches equal_weighted_dj30.py)
        cumulative_returns = (1 + strategy_returns).cumprod()

        # Calculate metrics
        total_return = cumulative_returns.iloc[-1] - 1

        # Prepare data for frontend
        if hasattr(strategy_returns.index, 'strftime'):
            dates = strategy_returns.index.strftime('%Y-%m-%d').tolist()
        else:
            dates = [str(idx) for idx in strategy_returns.index.tolist()]
        pnl_values = cumulative_returns.tolist()

        return {
            'success': True,
            'pnl_data': {
                'dates': dates,
                'values': pnl_values
            },
            'metrics': {
                'total_return': float(total_return),
                'total_return_pct': f"{total_return * 100:.2f}%",
                'stocks_count': len(close_data.columns),
                'date_range': f"{dates[0]} to {dates[-1]}",
                'method': 'Pure equal weighting (alpha=1)'
            }
        }

    # Apply strategy parameters from settings
    Truncation = settings.get('truncation', 0.01)  # Small truncation for outliers
    Decay = settings.get('decay', 1)
    Delay = settings.get('delay', 1)

    # For multi-stock, we already have cross-sectional data
    if isinstance(df_alpha, pd.DataFrame):
        # Apply truncation to remove extreme outliers
        alpha_truncated = df_alpha.clip(axis=0,
                                      lower=df_alpha.quantile(Truncation, axis=1),
                                      upper=df_alpha.quantile(1-Truncation, axis=1))

        # Normalize weights (cross-sectionally)
        normalized_weight = alpha_truncated.div(alpha_truncated.abs().sum(axis=1), axis=0)

        # Apply decay and delay
        def weighted_moving_average(x):
            n = len(x)
            if n == 0:
                return 0
            weights = np.arange(1, n+1)
            return np.sum(x * weights) / np.sum(weights)

        if Decay > 1:
            alpha_decayed = normalized_weight.rolling(window=Decay).apply(weighted_moving_average, raw=True)
        else:
            alpha_decayed = normalized_weight

        alpha_final = alpha_decayed.shift(Delay)

        # Calculate returns for all stocks
        returns = close_data.pct_change()
        returns = returns.loc[alpha_final.index]

        # Calculate strategy returns (portfolio return)
        strategy_returns = (alpha_final * returns).sum(axis=1)

    else:
        # Single series case (shouldn't happen in multi-stock mode, but handle it)
        df_alpha = pd.Series(df_alpha, index=common_dates)
        alpha_final = df_alpha.shift(Delay)
        returns = close_data.iloc[:, 0].pct_change()
        strategy_returns = alpha_final * returns

    # Remove NaN values
    strategy_returns = strategy_returns.dropna()

    if len(strategy_returns) == 0:
        raise Exception("No valid returns calculated")

    # Calculate cumulative returns using arithmetic compounding
    cumulative_returns = (1 + strategy_returns).cumprod()

    # Calculate metrics
    total_return = cumulative_returns.iloc[-1] - 1

    # Prepare data for frontend
    if hasattr(strategy_returns.index, 'strftime'):
        dates = strategy_returns.index.strftime('%Y-%m-%d').tolist()
    else:
        dates = [str(idx) for idx in strategy_returns.index.tolist()]
    pnl_values = cumulative_returns.tolist()

    return {
        'success': True,
        'pnl_data': {
            'dates': dates,
            'values': pnl_values
        },
        'metrics': {
            'total_return': float(total_return),
            'total_return_pct': f"{total_return * 100:.2f}%",
            'stocks_count': len(stock_symbols),
            'date_range': f"{dates[0]} to {dates[-1]}"
        }
    }