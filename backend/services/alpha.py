# backend/services/alpha.py
import numpy as np
import pandas as pd
import sympy as sp
import re

from django.core.cache import cache

# Import helper functions from utils/helpers.py
from utils.helpers import (
    Rank, Delta, Sum, Abs, Sqrt, Ts_argmax, Ts_rank, quantile_transform, trade_when, ts_sum, Returns, hump, ts_delta, bucket, group_neutralize, if_else,
    # Additional time-series operators
    ts_arg_min, ts_av_diff, ts_backfill,
    # Position sizing operators
    scale,
    # Arithmetic operators
    add, densify, divide, inverse, log, max_op, min_op, multiply, power, reverse, sign, signed_power, subtract,
    # Logical operators
    and_op, or_op, not_op, is_nan, lt_op, le_op, eq_op, gt_op, ge_op, ne_op
)

# Keys used by your services/state or cache layer (adjust if you use different keys)
DATA_KEY = "api:stored_data"
MULTI_KEY = "api:stored_multi_data"
SETTINGS_KEY = "api:strategy_settings"


def run_alpha_strategy(alpha_formula_str):
    """
    Orchestrator: reads cached data and settings and runs either single or multi stock processor.
    Returns the result dict expected by the frontend.
    """
    try:
        print(f"Processing alpha formula: {alpha_formula_str}")
        settings = cache.get(SETTINGS_KEY) or {}
        multi = cache.get(MULTI_KEY)
        single = cache.get(DATA_KEY)

        print(f"Settings: {settings}")
        print(f"Multi data available: {multi is not None}")
        print(f"Single data available: {single is not None}")

        if multi:
            print(f"Using multi-stock processing with {len(multi)} stocks")
            return process_alpha_strategy_multi(multi, alpha_formula_str, settings)
        elif single is not None:
            print(f"Using single-stock processing with {len(single)} rows")
            return process_alpha_strategy(single, alpha_formula_str, settings)
        else:
            raise ValueError("No data uploaded")
    except Exception as e:
        print(f"Error in run_alpha_strategy: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def _normalize_varnames(formula: str) -> str:
    """Case-insensitive replacements to map user formula tokens to Python variables used below."""
    mapping = {
        'close': 'Close', 'CLOSE': 'Close', 'Close': 'Close',
        'open': 'Open', 'OPEN': 'Open', 'Open': 'Open',
        'high': 'High', 'HIGH': 'High', 'High': 'High',
        'low': 'Low', 'LOW': 'Low', 'Low': 'Low',
        'volume': 'Volume', 'VOLUME': 'Volume', 'Volume': 'Volume',
        'vwap': 'Vwap', 'VWAP': 'Vwap', 'Vwap': 'Vwap'
    }
    # Replace all occurrences (simple safe approach)
    for k, v in mapping.items():
        formula = formula.replace(k, v)
    return formula

def _fix_formula_syntax(formula: str) -> str:
    """Fix common syntax issues in multi-statement formulas."""
    # Handle single-line multi-statement case first
    if '\n' not in formula:
        # Look for patterns like ")function(" which should be ");function("
        formula = re.sub(r'\)([a-zA-Z_][a-zA-Z0-9_]*\()', r');\1', formula)

    # Handle missing semicolons between statements
    lines = formula.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # If line contains assignment but no semicolon, and it's not the last line
        if '=' in line and not line.endswith((';', ')', ']', '}')):
            # Check if next line exists and starts with a function call or assignment
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and (next_line[0].isalpha() or next_line.startswith(('group_', 'trade_', 'bucket'))):
                    line += ';'

        fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def process_alpha_strategy(df: pd.DataFrame, alpha_formula_str: str, settings: dict):
    """
    Single-stock alpha processing.
    - df: pandas DataFrame with columns ['Open','High','Low','Close','Volume'] and Date index
    - alpha_formula_str: string formula submitted by user
    - settings: dict with keys 'truncation','decay','delay', etc.
    Returns: dict with 'success', 'pnl_data' (dates, values) and 'metrics'
    """
    # Basic validation
    required_columns = {'Open', 'High', 'Low', 'Close', 'Volume'}
    if not required_columns.issubset(set(df.columns)):
        raise ValueError(f"DataFrame missing one of required columns: {required_columns}")

    # Convert columns to float series
    High = df['High'].astype(float)
    Low = df['Low'].astype(float)
    Open = df['Open'].astype(float)
    Close = df['Close'].astype(float)
    Volume = df['Volume'].astype(float)

    # VWAP: Volume Weighted Average Price (daily VWAP calculation)
    with np.errstate(divide='ignore', invalid='ignore'):
        typical_price = (High + Low + Close) / 3
        vwap_numerator = (typical_price * Volume).expanding(min_periods=1).sum()
        vwap_denominator = Volume.expanding(min_periods=1).sum()
        Vwap = vwap_numerator / vwap_denominator
        Vwap = Vwap.ffill().fillna(typical_price)

    # Normalise formula text
    alpha_formula_clean = _normalize_varnames(alpha_formula_str)
    alpha_formula_clean = _fix_formula_syntax(alpha_formula_clean)

    # Prepare safe evaluation context for quantile and other helpers
    eval_context = {
        'Close': Close,
        'Open': Open,
        'High': High,
        'Low': Low,
        'Volume': Volume,
        'Vwap': Vwap,
        # helpers
        'Rank': Rank,
        'Delta': Delta,
        'Sum': Sum,
        'Abs': Abs,
        'Sqrt': Sqrt,
        'Ts_argmax': Ts_argmax,
        'Ts_rank': Ts_rank,
        # quantile_transform exposed as 'quantile' so formulas like quantile(...) work
        'quantile': quantile_transform,
        # conditional operators
        'trade_when': trade_when,
        'if_else': if_else,
        # logical operators - use function names to avoid conflicts with Python keywords
        'and': and_op,
        'or': or_op,
        'not': not_op,
        'is_nan': is_nan,
        # comparison operators (can also use native <, >, etc. but these are explicit functions)
        'lt': lt_op,
        'le': le_op,
        'eq': eq_op,
        'gt': gt_op,
        'ge': ge_op,
        'ne': ne_op,
        # additional helper functions
        'ts_sum': ts_sum,
        'Returns': Returns,
        'hump': hump,
        'ts_delta': ts_delta,
        'ts_arg_min': ts_arg_min,
        'ts_av_diff': ts_av_diff,
        'ts_backfill': ts_backfill,
        'scale': scale,
        # arithmetic operators
        'add': add,
        'densify': densify,
        'divide': divide,
        'inverse': inverse,
        'log': log,
        'max': max_op,
        'min': min_op,
        'multiply': multiply,
        'power': power,
        'reverse': reverse,
        'sign': sign,
        'signed_power': signed_power,
        'subtract': subtract,
        'bucket': bucket,
        'group_neutralize': group_neutralize,
        # convenience
        'pd': pd,
        'np': np
    }

    # Evaluate formula: two branches
    try:
        if 'quantile(' in alpha_formula_clean.lower():
            # For quantile expressions we use eval with quantile helper in context
            df_alpha = eval(alpha_formula_clean, {"__builtins__": {}}, eval_context)
        else:
            # For non-quantile formulas we try SymPy parsing and then eval the resulting expression string
            alpha_sym = sp.sympify(alpha_formula_clean)
            expr = str(alpha_sym)
            df_alpha = eval(expr, {"__builtins__": {}}, eval_context)

    except Exception as e:
        raise Exception(f"Error evaluating alpha formula: {str(e)}")

    # Apply strategy parameters (with defaults)
    Truncation = settings.get('truncation', 0)
    Decay = settings.get('decay', 1)
    Delay = settings.get('delay', 1)
    Neutralization = settings.get('neutralization', False)

    # Processing when result is a Series / numpy array (single time-series)
    if isinstance(df_alpha, (pd.Series, np.ndarray)):
        if isinstance(df_alpha, np.ndarray):
            df_alpha = pd.Series(df_alpha, index=Close.index)

        # Apply neutralization if enabled (for single series, this just centers around 0)
        if Neutralization:
            alpha_mean = df_alpha.mean()
            if not pd.isna(alpha_mean):
                df_alpha = df_alpha - alpha_mean

        # shift by Delay (implement execution lag)
        alpha_final = df_alpha.shift(Delay)

        # compute returns
        returns = Close.pct_change().reindex(alpha_final.index)

        # For single time series, normalize alpha to proper position sizing
        with np.errstate(divide='ignore', invalid='ignore'):
            alpha_abs = alpha_final.abs()
            alpha_normalized = alpha_final / alpha_abs
            # Replace NaN (from 0/0) with 0 (no position)
            alpha_normalized = alpha_normalized.fillna(0)

        strategy_returns = alpha_normalized * returns

    else:
        # Expect df_alpha to be DataFrame (cross-sectional-like) or convertible
        if not isinstance(df_alpha, pd.DataFrame):
            # if scalar numeric, convert to DataFrame with same index
            if isinstance(df_alpha, (int, float)):
                df_alpha = pd.Series([df_alpha] * len(Close), index=Close.index).to_frame(name='alpha')
            else:
                # try to coerce
                df_alpha = pd.DataFrame(df_alpha, index=Close.index)

        # Apply neutralization if enabled (subtract cross-sectional mean each day)
        if Neutralization:
            # For each time period, subtract the mean across all stocks
            alpha_means = df_alpha.mean(axis=1)
            df_alpha = df_alpha.sub(alpha_means, axis=0)

        # Apply truncation (row-wise quantile clipping to remove extreme outliers)
        if Truncation and 0 < Truncation < 0.5:
            lower = df_alpha.quantile(Truncation, axis=1)
            upper = df_alpha.quantile(1 - Truncation, axis=1)
            alpha_truncated = df_alpha.clip(lower=lower, upper=upper, axis=0)
        else:
            alpha_truncated = df_alpha.copy()

        # Normalize cross-sectionally to sum to 1 in absolute terms (per row)
        abs_sums = alpha_truncated.abs().sum(axis=1)
        # Handle zero sum case properly
        abs_sums = abs_sums.replace(0, np.nan)
        normalized_weight = alpha_truncated.div(abs_sums, axis=0)
        # Fill NaN with equal weights when all alphas are zero
        equal_weight = 1.0 / alpha_truncated.shape[1]
        normalized_weight = normalized_weight.fillna(equal_weight)

        # Apply decay (weighted moving average over the cross-sectional weights if decay>1)
        def _wma(x):
            n = len(x)
            if n <= 0:
                return 0
            weights = np.arange(1, n + 1)
            return np.sum(x * weights) / np.sum(weights)

        if Decay and Decay > 1:
            alpha_decayed = normalized_weight.rolling(window=Decay, min_periods=1).apply(_wma, raw=True)
        else:
            alpha_decayed = normalized_weight

        alpha_final = alpha_decayed.shift(Delay)

        # compute returns
        # For single-stock mode however, Close is a Series; in this branch we expect cross-section (shouldn't happen),
        # but keep compatibility by taking the first column if necessary
        if isinstance(Close, pd.Series):
            returns = Close.pct_change().reindex(alpha_final.index)
            # if alpha_final has a single column, multiply elementwise
            if alpha_final.shape[1] == 1:
                strategy_returns = alpha_final.iloc[:, 0] * returns
            else:
                # sum across columns (assume columns align)
                strategy_returns = (alpha_final * returns).sum(axis=1)
        else:
            # Close is series; fallback
            returns = Close.pct_change().reindex(alpha_final.index)
            strategy_returns = (alpha_final * returns).sum(axis=1)

    # Clean up and produce final metrics
    strategy_returns = strategy_returns.dropna()
    if len(strategy_returns) == 0:
        raise Exception("No valid returns calculated - check data quality and alpha formula")

    # Additional validation
    if np.isinf(strategy_returns).any():
        print("Warning: Infinite values detected in strategy returns, replacing with 0")
        strategy_returns = strategy_returns.replace([np.inf, -np.inf], 0)

    if strategy_returns.abs().max() > 1.0:
        print(f"Warning: Large daily return detected: {strategy_returns.abs().max():.4f}")

    # Calculate cumulative returns with proper handling
    try:
        cumulative_returns = (1 + strategy_returns).cumprod()
        total_return = cumulative_returns.iloc[-1] - 1
    except Exception as e:
        print(f"Error in cumulative return calculation: {e}")
        # Fallback calculation
        cumulative_returns = pd.Series([1.0] * len(strategy_returns), index=strategy_returns.index)
        total_return = 0.0

    # Dates for frontend
    if hasattr(strategy_returns.index, 'strftime'):
        dates = strategy_returns.index.strftime('%Y-%m-%d').tolist()
    else:
        dates = [str(idx) for idx in strategy_returns.index.tolist()]

    pnl_values = cumulative_returns.tolist()

    return {
        'success': True,
        'pnl_data': {'dates': dates, 'values': pnl_values},
        'metrics': {
            'total_return': float(total_return),
            'total_return_pct': f"{total_return * 100:.2f}%",
            'neutralization': 'On' if Neutralization else 'Off'
        }
    }


def process_alpha_strategy_multi(multi_stock_data: dict, alpha_formula_str: str, settings: dict):
    """
    Multi-stock processing. Accepts:
      - multi_stock_data: dict mapping symbol -> DataFrame (with Open, High, Low, Close, Volume)
      - alpha_formula_str: formula string
      - settings: dict
    Returns same structure as process_alpha_strategy.
    """
    # Extract stock symbols
    stock_symbols = list(multi_stock_data.keys())
    if len(stock_symbols) == 0:
        raise ValueError("No stocks provided in multi_stock_data")

    # Build aligned DataFrames for each price type
    close_data = pd.DataFrame({s: multi_stock_data[s]['Close'].astype(float) for s in stock_symbols})
    open_data = pd.DataFrame({s: multi_stock_data[s]['Open'].astype(float) for s in stock_symbols})
    high_data = pd.DataFrame({s: multi_stock_data[s]['High'].astype(float) for s in stock_symbols})
    low_data = pd.DataFrame({s: multi_stock_data[s]['Low'].astype(float) for s in stock_symbols})
    volume_data = pd.DataFrame({s: multi_stock_data[s]['Volume'].astype(float) for s in stock_symbols})

    # align to common dates (assumes load_dow30 already intersected; still enforce)
    common_index = close_data.index.intersection(open_data.index).intersection(high_data.index).intersection(low_data.index).intersection(volume_data.index)
    if len(common_index) == 0:
        raise ValueError("No common dates across stocks")

    close_data = close_data.loc[common_index].sort_index()
    open_data = open_data.loc[common_index].sort_index()
    high_data = high_data.loc[common_index].sort_index()
    low_data = low_data.loc[common_index].sort_index()
    volume_data = volume_data.loc[common_index].sort_index()

    # VWAP for all stocks (expanding window calculation)
    with np.errstate(divide='ignore', invalid='ignore'):
        typical_price_data = (high_data + low_data + close_data) / 3
        vwap_numerator = (typical_price_data * volume_data).expanding(min_periods=1).sum()
        vwap_denominator = volume_data.expanding(min_periods=1).sum()
        vwap_data = vwap_numerator / vwap_denominator
        vwap_data = vwap_data.ffill().fillna(typical_price_data)

    # Normalise formulas
    alpha_formula_clean = _normalize_varnames(alpha_formula_str)
    alpha_formula_clean = _fix_formula_syntax(alpha_formula_clean)

    # Prepare eval context for multi-stock (DataFrames)
    eval_context = {
        'Close': close_data,
        'Open': open_data,
        'High': high_data,
        'Low': low_data,
        'Volume': volume_data,
        'Vwap': vwap_data,
        'Rank': Rank,
        'Delta': Delta,
        'Sum': Sum,
        'Abs': Abs,
        'Sqrt': Sqrt,
        'Ts_argmax': Ts_argmax,
        'Ts_rank': Ts_rank,
        # quantile_transform can accept DataFrames and will apply row-wise
        'quantile': quantile_transform,
        # conditional operators
        'trade_when': trade_when,
        'if_else': if_else,
        # logical operators - use function names to avoid conflicts with Python keywords
        'and': and_op,
        'or': or_op,
        'not': not_op,
        'is_nan': is_nan,
        # comparison operators (can also use native <, >, etc. but these are explicit functions)
        'lt': lt_op,
        'le': le_op,
        'eq': eq_op,
        'gt': gt_op,
        'ge': ge_op,
        'ne': ne_op,
        # additional helper functions
        'ts_sum': ts_sum,
        'Returns': Returns,
        'hump': hump,
        'ts_delta': ts_delta,
        'ts_arg_min': ts_arg_min,
        'ts_av_diff': ts_av_diff,
        'ts_backfill': ts_backfill,
        'scale': scale,
        # arithmetic operators
        'add': add,
        'densify': densify,
        'divide': divide,
        'inverse': inverse,
        'log': log,
        'max': max_op,
        'min': min_op,
        'multiply': multiply,
        'power': power,
        'reverse': reverse,
        'sign': sign,
        'signed_power': signed_power,
        'subtract': subtract,
        'bucket': bucket,
        'group_neutralize': group_neutralize,
        'pd': pd,
        'np': np
    }

    # Evaluate formula (handle multi-statement expressions and complex operators)
    try:
        # Check if formula contains multi-statement operations (assignments, bucket, etc.)
        has_assignment = '=' in alpha_formula_clean and not any(op in alpha_formula_clean for op in ['==', '!=', '<=', '>='])
        has_complex_ops = any(op in alpha_formula_clean.lower() for op in ['bucket(', 'group_neutralize(', 'trade_when(', 'hump(', 'if_else(', 'and(', 'or(', 'not(', 'is_nan(', 'lt(', 'le(', 'eq(', 'gt(', 'ge(', 'ne(', 'ts_arg_min(', 'ts_av_diff(', 'ts_backfill(', 'scale(', 'add(', 'densify(', 'divide(', 'inverse(', 'log(', 'max(', 'min(', 'multiply(', 'power(', 'reverse(', 'sign(', 'signed_power(', 'subtract('])

        if has_assignment or has_complex_ops or 'quantile(' in alpha_formula_clean.lower():
            # Use direct eval for complex expressions
            # Create a safe execution environment
            exec_globals = {"__builtins__": {}}
            exec_locals = eval_context.copy()

            # Execute the formula
            exec(alpha_formula_clean, exec_globals, exec_locals)

            # Try to find the result variable or last expression
            # Look for common result variable names
            result_vars = ['result', 'alpha', 'df_alpha']
            df_alpha = None

            # Check if any standard result variables exist
            for var_name in result_vars:
                if var_name in exec_locals:
                    df_alpha = exec_locals[var_name]
                    break

            # If no standard result variable, try to find the last assignment
            if df_alpha is None:
                # Get all variables that are pandas objects
                pandas_vars = {k: v for k, v in exec_locals.items()
                             if isinstance(v, (pd.Series, pd.DataFrame)) and not k.startswith('_')}

                # Exclude input data variables
                input_vars = {'Open', 'High', 'Low', 'Close', 'Volume', 'Vwap', 'open_data', 'high_data', 'low_data', 'close_data', 'volume_data', 'vwap_data'}
                result_vars = {k: v for k, v in pandas_vars.items() if k not in input_vars}

                if result_vars:
                    # Take the last created variable (most likely the result)
                    df_alpha = list(result_vars.values())[-1]

            # If still no result, evaluate the last expression
            if df_alpha is None:
                # Split the formula into statements and get the last expression
                statements = [stmt.strip() for stmt in alpha_formula_clean.replace(';', '\n').split('\n') if stmt.strip()]
                if statements:
                    last_statement = statements[-1]
                    # If last statement is not an assignment, evaluate it
                    if '=' not in last_statement or any(op in last_statement for op in ['==', '!=', '<=', '>=']):
                        df_alpha = eval(last_statement, {"__builtins__": {}}, exec_locals)
                    else:
                        # If it's an assignment, try to evaluate the whole thing as one expression
                        try:
                            df_alpha = eval(alpha_formula_clean, {"__builtins__": {}}, eval_context)
                        except:
                            # Fallback: return the first pandas object found
                            pandas_vars = {k: v for k, v in exec_locals.items()
                                         if isinstance(v, (pd.Series, pd.DataFrame)) and not k.startswith('_')}
                            if pandas_vars:
                                df_alpha = list(pandas_vars.values())[-1]

        else:
            # Use sympy for simple expressions
            alpha_sym = sp.sympify(alpha_formula_clean)
            expr = str(alpha_sym)
            df_alpha = eval(expr, {"__builtins__": {}}, eval_context)

    except Exception as e:
        raise Exception(f"Error evaluating alpha formula: {str(e)}")

    # Handle scalar alpha (e.g., user provided "1")
    if isinstance(df_alpha, (int, float)):
        df_alpha = pd.DataFrame(
            np.full(close_data.shape, df_alpha),
            index=close_data.index,
            columns=close_data.columns
        )

    # If dataframe all ones => pure equal weight special-case (consistent with equal_weighted_dj30.py)
    if isinstance(df_alpha, pd.DataFrame) and ((df_alpha == 1).all().all()):
        returns = close_data.pct_change().dropna()
        # Equal weighted portfolio return: arithmetic mean of all stock returns (matching equal_weighted_dj30.py:179)
        strategy_returns = returns.mean(axis=1).dropna()
        if len(strategy_returns) == 0:
            raise Exception("No valid returns calculated")

        # Validation consistent with other calculation paths
        if np.isinf(strategy_returns).any():
            print("Warning: Infinite values detected in equal-weight returns, replacing with 0")
            strategy_returns = strategy_returns.replace([np.inf, -np.inf], 0)

        cumulative_returns = (1 + strategy_returns).cumprod()
        total_return = cumulative_returns.iloc[-1] - 1

        dates = strategy_returns.index.strftime('%Y-%m-%d').tolist() if hasattr(strategy_returns.index, 'strftime') else [str(i) for i in strategy_returns.index]
        return {
            'success': True,
            'pnl_data': {'dates': dates, 'values': cumulative_returns.tolist()},
            'metrics': {
                'total_return': float(total_return),
                'total_return_pct': f"{total_return * 100:.2f}%",
                'stocks_count': len(close_data.columns),
                'date_range': f"{dates[0]} to {dates[-1]}",
                'method': 'Pure equal weighting (alpha=1) - matches equal_weighted_dj30.py logic',
                'neutralization': 'On' if Neutralization else 'Off'
            }
        }

    # Settings
    Truncation = settings.get('truncation', 0.01)
    Decay = settings.get('decay', 1)
    Delay = settings.get('delay', 1)
    Neutralization = settings.get('neutralization', False)

    # If result is DataFrame (preferred)
    if isinstance(df_alpha, pd.DataFrame):
        # Apply neutralization if enabled (subtract cross-sectional mean each day)
        if Neutralization:
            # For each time period, subtract the mean across all stocks
            alpha_means = df_alpha.mean(axis=1)
            df_alpha = df_alpha.sub(alpha_means, axis=0)

        # Clip row-wise to remove outliers
        if Truncation and 0 < Truncation < 0.5:
            lower = df_alpha.quantile(Truncation, axis=1)
            upper = df_alpha.quantile(1 - Truncation, axis=1)
            alpha_truncated = df_alpha.clip(lower=lower, upper=upper, axis=0)
        else:
            alpha_truncated = df_alpha.copy()

        # Normalize cross-sectionally to sum to 1 in absolute terms
        abs_sums = alpha_truncated.abs().sum(axis=1)
        # Handle zero sum case properly
        abs_sums = abs_sums.replace(0, np.nan)
        normalized_weight = alpha_truncated.div(abs_sums, axis=0)
        # Fill NaN with equal weights when all alphas are zero
        equal_weight = 1.0 / alpha_truncated.shape[1]
        normalized_weight = normalized_weight.fillna(equal_weight)

        # Weighted moving average for decay
        def _wma(x):
            n = len(x)
            if n <= 0:
                return 0
            weights = np.arange(1, n + 1)
            return np.sum(x * weights) / np.sum(weights)

        if Decay and Decay > 1:
            alpha_decayed = normalized_weight.rolling(window=Decay, min_periods=1).apply(_wma, raw=True)
        else:
            alpha_decayed = normalized_weight

        alpha_final = alpha_decayed.shift(Delay)

        # Calculate returns and portfolio returns
        returns = close_data.pct_change()
        returns = returns.reindex(alpha_final.index)

        # Calculate portfolio returns: element-wise product of weights and returns, then sum
        # Check weights normalization (should sum to 1 in absolute terms)
        portfolio_weights_check = alpha_final.abs().sum(axis=1).dropna()
        if len(portfolio_weights_check) > 0:
            weights_mean = portfolio_weights_check.mean()
            if not np.isclose(weights_mean, 1.0, atol=1e-3):
                print(f"Warning: Portfolio weights average {weights_mean:.6f}, expected ~1.0")
                # Renormalize if significantly off
                if abs(weights_mean - 1.0) > 0.1:
                    print("Renormalizing portfolio weights")
                    alpha_final = alpha_final.div(portfolio_weights_check, axis=0)

        strategy_returns = (alpha_final * returns).sum(axis=1)

    else:
        # If df_alpha is a Series-like, treat as single-series alpha applied to first column
        if isinstance(df_alpha, (pd.Series, np.ndarray)):
            if isinstance(df_alpha, np.ndarray):
                df_alpha = pd.Series(df_alpha, index=close_data.index)
            alpha_final = pd.Series(df_alpha).shift(Delay)
            returns = close_data.iloc[:, 0].pct_change().reindex(alpha_final.index)
            strategy_returns = alpha_final * returns
        else:
            raise Exception("Unhandled alpha type in multi-stock processing")

    strategy_returns = strategy_returns.dropna()
    if len(strategy_returns) == 0:
        raise Exception("No valid returns calculated - check data quality and alpha formula")

    # Additional validation for multi-stock case
    if np.isinf(strategy_returns).any():
        print("Warning: Infinite values detected in strategy returns, replacing with 0")
        strategy_returns = strategy_returns.replace([np.inf, -np.inf], 0)

    if strategy_returns.abs().max() > 1.0:
        print(f"Warning: Large daily return detected: {strategy_returns.abs().max():.4f}")

    # Calculate cumulative returns with proper handling
    try:
        cumulative_returns = (1 + strategy_returns).cumprod()
        total_return = cumulative_returns.iloc[-1] - 1
    except Exception as e:
        print(f"Error in cumulative return calculation: {e}")
        # Fallback calculation
        cumulative_returns = pd.Series([1.0] * len(strategy_returns), index=strategy_returns.index)
        total_return = 0.0

    if hasattr(strategy_returns.index, 'strftime'):
        dates = strategy_returns.index.strftime('%Y-%m-%d').tolist()
    else:
        dates = [str(i) for i in strategy_returns.index]

    return {
        'success': True,
        'pnl_data': {'dates': dates, 'values': cumulative_returns.tolist()},
        'metrics': {
            'total_return': float(total_return),
            'total_return_pct': f"{total_return * 100:.2f}%",
            'stocks_count': len(stock_symbols),
            'date_range': f"{dates[0]} to {dates[-1]}",
            'neutralization': 'On' if Neutralization else 'Off'
        }
    }
