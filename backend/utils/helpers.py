import pandas as pd
import numpy as np
from scipy.stats import norm, cauchy, uniform

def Rank(x):
    """Cross-sectional rank function with proper edge case handling"""
    if isinstance(x, pd.Series):
        n = len(x)
        if n <= 1:
            return pd.Series([0.5] * n, index=x.index) if n == 1 else pd.Series([], dtype=float)
        ranks = x.rank(method='average', na_option='keep')
        return (ranks - 1) / (n - 1)
    else:
        # DataFrame case
        n_cols = x.shape[1]
        if n_cols <= 1:
            return pd.DataFrame(0.5, index=x.index, columns=x.columns)
        ranks = x.rank(axis=1, method='average', na_option='keep')
        return (ranks - 1) / (n_cols - 1)

def Delta(x, n):
    return x - x.shift(n)

def Sum(x, n):
    return x.rolling(n).sum()

def Abs(x):
    return x.abs()

def Sqrt(x):
    """Safe square root function that handles negative values"""
    if isinstance(x, pd.Series):
        return x.clip(lower=0).apply(np.sqrt)
    else:
        return x.clip(lower=0).apply(np.sqrt)

def Ts_argmax(x, n):
    return x.rolling(n).apply(lambda arr: int(np.nanargmax(arr)))

def Ts_rank(x, n):
    """Time-series rank: rank of current value within past n periods"""
    def _ts_rank_calc(window_vals):
        if len(window_vals) == 0 or np.isnan(window_vals[-1]):
            return np.nan

        # Convert to series for proper ranking
        series = pd.Series(window_vals)
        ranks = series.rank(method='average', na_option='keep')

        if len(ranks) <= 1:
            return 0.5

        # Return normalized rank of the last (current) value
        current_rank = ranks.iloc[-1]
        return (current_rank - 1) / (len(ranks) - 1)

    return x.rolling(window=n, min_periods=1).apply(_ts_rank_calc, raw=True)

def quantile_transform(series_or_row, driver="gaussian", sigma=1.0):
    # same logic you had but compacted and tested
    if isinstance(series_or_row, np.ndarray):
        series_or_row = pd.Series(series_or_row)
    if isinstance(series_or_row, pd.Series):
        N = len(series_or_row)
        ranked = (series_or_row.rank() - 1) / (N - 1)
        shifted = (1/N) + ranked * (1 - 2/N)
        if driver.lower() == "uniform":
            return (shifted - shifted.mean()) * sigma
        if driver.lower() == "gaussian":
            return norm.ppf(shifted) * sigma
        if driver.lower() == "cauchy":
            return cauchy.ppf(shifted) * sigma
        raise ValueError("Unknown driver")
    else:
        return series_or_row.apply(lambda row: quantile_transform(row.dropna(), driver=driver, sigma=sigma), axis=1)

def trade_when(trigger_trade_exp, alpha_exp, trigger_exit_exp=None):
    """
    Conditional alpha assignment operator.

    Logic:
    - If trigger_exit_exp > 0: Alpha = NaN (close positions)
    - Else if trigger_trade_exp > 0: Alpha = alpha_exp (new positions)
    - Else: Alpha = previous_alpha (hold positions)

    Parameters:
    - trigger_trade_exp: Boolean/numeric condition for entering trades
    - alpha_exp: Alpha values to use when entering trades
    - trigger_exit_exp: Boolean/numeric condition for exiting trades (optional)

    Returns:
    - Series/DataFrame with conditional alpha values
    """
    # Handle both Series and DataFrame inputs
    if isinstance(trigger_trade_exp, (pd.Series, pd.DataFrame)):
        result = trigger_trade_exp.copy() * 0.0  # Initialize with zeros, same shape/index

        # Store previous alpha values (initialize as NaN)
        previous_alpha = result.copy()
        previous_alpha[:] = np.nan

        # Process each time step
        if isinstance(result, pd.Series):
            # Series case (single stock)
            for i, idx in enumerate(result.index):
                # Check exit condition first
                if trigger_exit_exp is not None:
                    exit_val = trigger_exit_exp.iloc[i] if hasattr(trigger_exit_exp, 'iloc') else trigger_exit_exp
                    if pd.notna(exit_val) and exit_val > 0:
                        result.iloc[i] = np.nan
                        previous_alpha.iloc[i] = np.nan
                        continue

                # Check trade condition
                trade_val = trigger_trade_exp.iloc[i] if hasattr(trigger_trade_exp, 'iloc') else trigger_trade_exp
                if pd.notna(trade_val) and trade_val > 0:
                    # New trade: use alpha_exp
                    alpha_val = alpha_exp.iloc[i] if hasattr(alpha_exp, 'iloc') else alpha_exp
                    result.iloc[i] = alpha_val
                    previous_alpha.iloc[i] = alpha_val
                else:
                    # Hold: use previous alpha
                    if i > 0:
                        result.iloc[i] = previous_alpha.iloc[i-1]
                        previous_alpha.iloc[i] = previous_alpha.iloc[i-1]
                    else:
                        result.iloc[i] = np.nan
                        previous_alpha.iloc[i] = np.nan

        else:
            # DataFrame case (multi-stock)
            for i in range(len(result)):
                # Check exit condition first
                if trigger_exit_exp is not None:
                    exit_condition = trigger_exit_exp.iloc[i] if hasattr(trigger_exit_exp, 'iloc') else trigger_exit_exp
                    if isinstance(exit_condition, (pd.Series, np.ndarray)):
                        exit_mask = exit_condition > 0
                    else:
                        exit_mask = exit_condition > 0

                    if isinstance(exit_mask, (bool, np.bool_)) and exit_mask:
                        result.iloc[i] = np.nan
                        previous_alpha.iloc[i] = np.nan
                        continue
                    elif hasattr(exit_mask, '__iter__') and exit_mask.any():
                        result.iloc[i][exit_mask] = np.nan
                        previous_alpha.iloc[i][exit_mask] = np.nan

                # Check trade condition
                trade_condition = trigger_trade_exp.iloc[i] if hasattr(trigger_trade_exp, 'iloc') else trigger_trade_exp
                if isinstance(trade_condition, (pd.Series, np.ndarray)):
                    trade_mask = trade_condition > 0
                else:
                    trade_mask = trade_condition > 0

                alpha_vals = alpha_exp.iloc[i] if hasattr(alpha_exp, 'iloc') else alpha_exp

                if isinstance(trade_mask, (bool, np.bool_)):
                    if trade_mask:
                        result.iloc[i] = alpha_vals
                        previous_alpha.iloc[i] = alpha_vals
                    else:
                        # Hold previous
                        if i > 0:
                            result.iloc[i] = previous_alpha.iloc[i-1]
                            previous_alpha.iloc[i] = previous_alpha.iloc[i-1]
                        else:
                            result.iloc[i] = np.nan
                            previous_alpha.iloc[i] = np.nan
                else:
                    # Element-wise processing
                    new_trade_positions = trade_mask & pd.notna(alpha_vals)
                    hold_positions = ~trade_mask

                    # Set new trades
                    result.iloc[i][new_trade_positions] = alpha_vals[new_trade_positions]
                    previous_alpha.iloc[i][new_trade_positions] = alpha_vals[new_trade_positions]

                    # Hold previous positions
                    if i > 0:
                        result.iloc[i][hold_positions] = previous_alpha.iloc[i-1][hold_positions]
                        previous_alpha.iloc[i][hold_positions] = previous_alpha.iloc[i-1][hold_positions]
                    else:
                        result.iloc[i][hold_positions] = np.nan
                        previous_alpha.iloc[i][hold_positions] = np.nan

        return result

    else:
        # Scalar case - convert to boolean logic
        if trigger_exit_exp is not None and trigger_exit_exp > 0:
            return np.nan
        elif trigger_trade_exp > 0:
            return alpha_exp
        else:
            return np.nan  # No previous value for scalar case

def ts_sum(x, n):
    """Time-series sum over n periods (rolling sum)"""
    return x.rolling(window=n, min_periods=1).sum()

def Returns(x, n=1):
    """Calculate returns over n periods"""
    return x.pct_change(periods=n)

def hump(alpha_values, hump_threshold=0.01):
    """
    Limits the frequency and magnitude of changes in Alpha values (reducing turnover).

    Logic:
    1. Calculate change = today's value - yesterday's value
    2. Calculate limit = hump_threshold × group_sum(abs(alpha_values), market)
    3. If abs(change) < limit: retain yesterday's value
    4. Else: new_value = yesterday's value + sign(change) × limit

    Parameters:
    - alpha_values: Series/DataFrame of alpha values
    - hump_threshold: threshold parameter (default 0.01)

    Returns:
    - Series/DataFrame with smoothed alpha values
    """
    if isinstance(alpha_values, pd.Series):
        # Series case (single stock)
        result = alpha_values.copy()

        for i in range(1, len(result)):
            yesterday_value = result.iloc[i-1]
            today_value = alpha_values.iloc[i]

            if pd.isna(yesterday_value) or pd.isna(today_value):
                continue

            change = today_value - yesterday_value

            # For single series, limit is based on absolute value of current alpha
            limit = hump_threshold * abs(today_value) if abs(today_value) > 0 else hump_threshold

            if abs(change) < limit:
                # Retain yesterday's value
                result.iloc[i] = yesterday_value
            else:
                # Apply limited change
                result.iloc[i] = yesterday_value + np.sign(change) * limit

        return result

    elif isinstance(alpha_values, pd.DataFrame):
        # DataFrame case (multi-stock)
        result = alpha_values.copy()

        for i in range(1, len(result)):
            yesterday_values = result.iloc[i-1]
            today_values = alpha_values.iloc[i]

            # Calculate cross-sectional limit (sum of absolute alpha values)
            market_abs_sum = abs(today_values).sum()
            limit = hump_threshold * market_abs_sum if market_abs_sum > 0 else hump_threshold

            # Calculate changes
            changes = today_values - yesterday_values

            # Apply hump logic element-wise
            for col in result.columns:
                if pd.isna(yesterday_values[col]) or pd.isna(today_values[col]):
                    continue

                change = changes[col]

                if abs(change) < limit:
                    # Retain yesterday's value
                    result.iloc[i, result.columns.get_loc(col)] = yesterday_values[col]
                else:
                    # Apply limited change
                    result.iloc[i, result.columns.get_loc(col)] = yesterday_values[col] + np.sign(change) * limit

        return result

    else:
        # Scalar case - no smoothing possible
        return alpha_values

def ts_delta(x, n=1):
    """Calculate difference between current value and value n periods ago"""
    return x - x.shift(n)
