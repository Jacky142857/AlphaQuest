import pandas as pd
import numpy as np


def Delta(x, n):
    return x - x.shift(n)


def Sum(x, n):
    return x.rolling(n).sum()


def Ts_argmax(x, n):
    return x.rolling(n).apply(lambda arr: int(np.nanargmax(arr)))


def ts_arg_min(x, d):
    """
    Returns the relative index of the min value in the time series for the past d days.
    If the current day has the min value for the past d days, it returns 0.
    If previous day has the min value for the past d days, it returns 1.
    """
    def _ts_arg_min_calc(window_vals):
        if len(window_vals) == 0:
            return np.nan

        # Find the index of minimum value (earliest occurrence if ties)
        min_idx = np.nanargmin(window_vals)

        # Return relative index from current (last) position
        # If min is at last position (today), return 0
        # If min is at second-to-last position (yesterday), return 1, etc.
        return len(window_vals) - 1 - min_idx

    return x.rolling(window=d, min_periods=1).apply(_ts_arg_min_calc, raw=True)


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


def ts_av_diff(x, d):
    """
    Returns x - ts_mean(x, d), but it deals with NaNs carefully.
    That is NaNs are ignored during mean computation.

    Example:
    If d = 6 and values for past 6 days are [6,2,8,5,9,NaN] then ts_mean(x,d) = 6
    since NaN are ignored from mean computation. Hence, ts_av_diff(x,d) = 6-6 = 0
    """
    def _ts_mean_ignoring_nan(window_vals):
        """Calculate mean while ignoring NaN values"""
        if len(window_vals) == 0:
            return np.nan

        # Remove NaN values
        clean_vals = window_vals[~np.isnan(window_vals)]

        if len(clean_vals) == 0:
            return np.nan

        return np.mean(clean_vals)

    # Calculate rolling mean ignoring NaNs
    ts_mean = x.rolling(window=d, min_periods=1).apply(_ts_mean_ignoring_nan, raw=True)

    # Return x - ts_mean
    return x - ts_mean


def ts_backfill(x, lookback=252, k=1, ignore="NAN"):
    """
    Backfill is the process of replacing the NaN or 0 values by a meaningful value (i.e., a first non-NaN value).

    The ts_backfill operator replaces NaN values with the last available non-NaN value. If the input value
    of the data field x is NaN, the ts_backfill operator will check available input values of the same data
    field for the past d number of days, and output the most recent available non-NaN input value. If the
    k parameter is set, then the ts_backfill operator will output the kth most recent available non-NaN
    input value.

    This operator improves weight coverage and may help to reduce drawdown risk.

    Parameters:
    - x: Input time series
    - lookback: Number of days to look back (default 252)
    - k: Which recent non-NaN value to use (1 = most recent, 2 = second most recent, etc.)
    - ignore: What values to ignore ("NAN" for NaN values, could be extended for other values)

    Example: ts_backfill(x, 252)
    - If the input value for data field x = non-NaN, then output = x
    - If the input value for data field x = NaN, then output = most recent available non-NaN input value for x
      in the past 252 days
    """
    if isinstance(x, pd.Series):
        result = x.copy()

        for i in range(len(x)):
            current_val = x.iloc[i]

            # Check if current value needs to be backfilled
            if ignore == "NAN" and pd.isna(current_val):
                # Look back for the kth most recent non-NaN value
                start_idx = max(0, i - lookback)
                lookback_window = x.iloc[start_idx:i]

                # Find non-NaN values in reverse order (most recent first)
                non_nan_values = lookback_window.dropna()

                if len(non_nan_values) >= k:
                    # Get the kth most recent value (k=1 means most recent)
                    result.iloc[i] = non_nan_values.iloc[-(k)]
                # If not enough non-NaN values found, keep the NaN

        return result

    elif isinstance(x, pd.DataFrame):
        # Apply to each column independently
        result = x.copy()

        for col in x.columns:
            result[col] = ts_backfill(x[col], lookback=lookback, k=k, ignore=ignore)

        return result

    else:
        # Scalar case - if it's NaN and we have no history, return NaN
        if ignore == "NAN" and pd.isna(x):
            return np.nan
        else:
            return x