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

def bucket(x, buckets=None, range=None, skipBegin=False, skipEnd=False, skipBoth=False, NANGroup=False):
    """
    Convert float values into indices for user-specified buckets.

    Parameters:
    - x: Series/DataFrame with float values to bucket
    - buckets: List/string of bucket boundaries (e.g., "2,5,6,7,10" or [2,5,6,7,10])
    - range: String format "start,end,step" (e.g., "0.1,1,0.1")
    - skipBegin: Remove the (-inf, start] bucket
    - skipEnd: Remove the [end, +inf) bucket
    - skipBoth: Remove both edge buckets (same as skipBegin=True, skipEnd=True)
    - NANGroup: Assign NaN values to a separate group (index after last bucket)

    Returns:
    - Series/DataFrame with bucket indices (0, 1, 2, ...)
    """

    if buckets is not None and range is not None:
        raise ValueError("Cannot specify both 'buckets' and 'range' parameters")

    if buckets is None and range is None:
        raise ValueError("Must specify either 'buckets' or 'range' parameter")

    # Parse buckets parameter
    if buckets is not None:
        if isinstance(buckets, str):
            bucket_list = [float(b.strip()) for b in buckets.split(',')]
        else:
            bucket_list = list(buckets)

    # Parse range parameter
    elif range is not None:
        if isinstance(range, str):
            parts = [float(p.strip()) for p in range.split(',')]
            if len(parts) != 3:
                raise ValueError("Range must be in format 'start,end,step'")
            start, end, step = parts
        else:
            start, end, step = range

        # Generate bucket boundaries
        bucket_list = []
        current = start
        while current <= end:
            bucket_list.append(current)
            current += step

    # Handle skipBoth parameter
    if skipBoth:
        skipBegin = True
        skipEnd = True

    # Create bucket boundaries with edge buckets
    boundaries = [-np.inf] + sorted(bucket_list) + [np.inf]

    # Remove edge buckets if requested
    if skipBegin:
        boundaries = boundaries[1:]  # Remove -inf bucket
    if skipEnd:
        boundaries = boundaries[:-1]  # Remove +inf bucket

    def _bucket_values(series):
        """Apply bucketing to a single series"""
        # Handle NaN values
        nan_mask = pd.isna(series)

        # Use pd.cut to assign bucket indices
        try:
            bucket_indices = pd.cut(series, bins=boundaries, labels=False, include_lowest=True)
        except ValueError:
            # If all values are NaN or other edge case
            bucket_indices = pd.Series([np.nan] * len(series), index=series.index)

        # Handle NaN group
        if NANGroup:
            max_bucket_idx = len(boundaries) - 2 if len(boundaries) > 1 else 0
            nan_group_idx = max_bucket_idx + 1
            bucket_indices = bucket_indices.fillna(nan_group_idx)

        return bucket_indices

    # Apply bucketing
    if isinstance(x, pd.Series):
        return _bucket_values(x)
    elif isinstance(x, pd.DataFrame):
        result = pd.DataFrame(index=x.index, columns=x.columns)
        for col in x.columns:
            result[col] = _bucket_values(x[col])
        return result
    else:
        # Handle scalar or numpy array
        if isinstance(x, (int, float)):
            # Single value
            if pd.isna(x):
                if NANGroup:
                    return len(boundaries) - 1
                else:
                    return np.nan

            # Find which bucket the value falls into
            for i, boundary in enumerate(boundaries[1:]):
                if x <= boundary:
                    return i
            return len(boundaries) - 2  # Last bucket
        else:
            # Convert to Series and process
            temp_series = pd.Series(x)
            return _bucket_values(temp_series).values

def if_else(condition, alpha_expression_1, alpha_expression_2):
    """
    Conditional operator that returns alpha_expression_1 when condition is true,
    otherwise returns alpha_expression_2.

    Parameters:
    - condition: Boolean expression/condition to evaluate
    - alpha_expression_1: Alpha values to use when condition is true
    - alpha_expression_2: Alpha values to use when condition is false

    Returns:
    - Series/DataFrame with conditional alpha values
    """
    # Convert condition to boolean if it's numeric (> 0 means True)
    if isinstance(condition, (pd.Series, pd.DataFrame)):
        bool_condition = condition > 0
    else:
        # Scalar case
        bool_condition = condition > 0

    # Handle different input types
    if isinstance(bool_condition, pd.Series):
        # Series case (single stock)
        result = bool_condition.copy().astype(float)

        # Where condition is True, use alpha_expression_1
        if hasattr(alpha_expression_1, 'loc'):
            result.loc[bool_condition] = alpha_expression_1.loc[bool_condition]
        else:
            result.loc[bool_condition] = alpha_expression_1

        # Where condition is False, use alpha_expression_2
        if hasattr(alpha_expression_2, 'loc'):
            result.loc[~bool_condition] = alpha_expression_2.loc[~bool_condition]
        else:
            result.loc[~bool_condition] = alpha_expression_2

        return result

    elif isinstance(bool_condition, pd.DataFrame):
        # DataFrame case (multi-stock)
        result = bool_condition.copy().astype(float)

        # Apply condition element-wise
        if isinstance(alpha_expression_1, (pd.Series, pd.DataFrame)):
            result = result.where(~bool_condition, alpha_expression_1)
        else:
            result = result.where(~bool_condition, alpha_expression_1)

        if isinstance(alpha_expression_2, (pd.Series, pd.DataFrame)):
            result = result.where(bool_condition, alpha_expression_2)
        else:
            result = result.where(bool_condition, alpha_expression_2)

        return result

    else:
        # Scalar case
        if bool_condition:
            return alpha_expression_1
        else:
            return alpha_expression_2

# Logical operators
def and_op(input1, input2):
    """
    Logical AND operator. Returns true if both operands are true and returns false otherwise.
    Converts inputs to boolean: > 0 means True, <= 0 means False
    """
    if isinstance(input1, (pd.Series, pd.DataFrame)) or isinstance(input2, (pd.Series, pd.DataFrame)):
        bool1 = input1 > 0 if isinstance(input1, (pd.Series, pd.DataFrame)) else (input1 > 0)
        bool2 = input2 > 0 if isinstance(input2, (pd.Series, pd.DataFrame)) else (input2 > 0)
        result = bool1 & bool2
        return result.astype(int) if isinstance(result, (pd.Series, pd.DataFrame)) else int(result)
    else:
        return int((input1 > 0) and (input2 > 0))

def or_op(input1, input2):
    """
    Logical OR operator. Returns true if either or both inputs are true and returns false otherwise.
    """
    if isinstance(input1, (pd.Series, pd.DataFrame)) or isinstance(input2, (pd.Series, pd.DataFrame)):
        bool1 = input1 > 0 if isinstance(input1, (pd.Series, pd.DataFrame)) else (input1 > 0)
        bool2 = input2 > 0 if isinstance(input2, (pd.Series, pd.DataFrame)) else (input2 > 0)
        result = bool1 | bool2
        return result.astype(int) if isinstance(result, (pd.Series, pd.DataFrame)) else int(result)
    else:
        return int((input1 > 0) or (input2 > 0))

def not_op(x):
    """
    Returns the logical negation of x. If x is true (1), it returns false (0), and if input is false (0), it returns true (1).
    """
    if isinstance(x, (pd.Series, pd.DataFrame)):
        bool_x = x > 0
        result = ~bool_x
        return result.astype(int)
    else:
        return int(not (x > 0))

def is_nan(input_val):
    """
    If input == NaN return 1 else return 0
    """
    if isinstance(input_val, (pd.Series, pd.DataFrame)):
        result = pd.isna(input_val)
        return result.astype(int)
    else:
        return int(pd.isna(input_val))

# Comparison operators (these work with pandas naturally, but we'll provide explicit functions for clarity)
def lt_op(input1, input2):
    """
    If input1 < input2 return true, else return false
    """
    result = input1 < input2
    if isinstance(result, (pd.Series, pd.DataFrame)):
        return result.astype(int)
    else:
        return int(result)

def le_op(input1, input2):
    """
    Returns true if input1 <= input2, return false otherwise
    """
    result = input1 <= input2
    if isinstance(result, (pd.Series, pd.DataFrame)):
        return result.astype(int)
    else:
        return int(result)

def eq_op(input1, input2):
    """
    Returns true if both inputs are same and returns false otherwise
    """
    result = input1 == input2
    if isinstance(result, (pd.Series, pd.DataFrame)):
        return result.astype(int)
    else:
        return int(result)

def gt_op(input1, input2):
    """
    Logic comparison operators to compares two inputs
    """
    result = input1 > input2
    if isinstance(result, (pd.Series, pd.DataFrame)):
        return result.astype(int)
    else:
        return int(result)

def ge_op(input1, input2):
    """
    Returns true if input1 >= input2, return false otherwise
    """
    result = input1 >= input2
    if isinstance(result, (pd.Series, pd.DataFrame)):
        return result.astype(int)
    else:
        return int(result)

def ne_op(input1, input2):
    """
    Returns true if both inputs are NOT the same and returns false otherwise
    """
    result = input1 != input2
    if isinstance(result, (pd.Series, pd.DataFrame)):
        return result.astype(int)
    else:
        return int(result)

# Additional arithmetic operators
def add(*args, filter=False):
    """
    Add all inputs (at least 2 inputs required). If filter = true, filter all input NaN to 0 before adding.
    """
    if len(args) < 2:
        raise ValueError("add requires at least 2 inputs")

    result = args[0].copy() if hasattr(args[0], 'copy') else args[0]

    if filter:
        # Replace NaN with 0 before adding
        if isinstance(result, (pd.Series, pd.DataFrame)):
            result = result.fillna(0)

    for arg in args[1:]:
        if filter and isinstance(arg, (pd.Series, pd.DataFrame)):
            arg_clean = arg.fillna(0)
            result = result + arg_clean
        else:
            result = result + arg

    return result

def densify(x):
    """
    Converts a grouping field of many buckets into lesser number of only available buckets
    so as to make working with grouping fields computationally efficient.
    """
    if isinstance(x, (pd.Series, pd.DataFrame)):
        if isinstance(x, pd.Series):
            # Get unique values and create mapping to dense indices
            unique_vals = x.dropna().unique()
            unique_vals = np.sort(unique_vals)

            # Create mapping from original values to dense indices
            value_to_dense = {val: i for i, val in enumerate(unique_vals)}

            # Apply mapping
            result = x.copy()
            for val, dense_idx in value_to_dense.items():
                result[x == val] = dense_idx

            return result
        else:
            # DataFrame case - apply to each column
            result = x.copy()
            for col in x.columns:
                result[col] = densify(x[col])
            return result
    else:
        return x

def divide(x, y):
    """x / y"""
    if isinstance(x, (pd.Series, pd.DataFrame)) or isinstance(y, (pd.Series, pd.DataFrame)):
        return x / y
    else:
        return x / y if y != 0 else np.nan

def inverse(x):
    """1 / x"""
    if isinstance(x, (pd.Series, pd.DataFrame)):
        with np.errstate(divide='ignore', invalid='ignore'):
            result = 1.0 / x
            # Replace inf with NaN
            if isinstance(result, pd.Series):
                result = result.replace([np.inf, -np.inf], np.nan)
            else:
                result = result.replace([np.inf, -np.inf], np.nan)
        return result
    else:
        return 1.0 / x if x != 0 else np.nan

def log(x):
    """
    Natural logarithm. For example: Log(high/low) uses natural logarithm of high/low ratio as stock weights.
    """
    if isinstance(x, (pd.Series, pd.DataFrame)):
        with np.errstate(divide='ignore', invalid='ignore'):
            result = np.log(x)
            return result
    else:
        return np.log(x) if x > 0 else np.nan

def max_op(*args):
    """
    Maximum value of all inputs. At least 2 inputs are required.
    """
    if len(args) < 2:
        raise ValueError("max requires at least 2 inputs")

    result = args[0]
    for arg in args[1:]:
        if isinstance(result, (pd.Series, pd.DataFrame)) or isinstance(arg, (pd.Series, pd.DataFrame)):
            result = np.maximum(result, arg)
        else:
            result = max(result, arg)

    return result

def min_op(*args):
    """
    Minimum value of all inputs. At least 2 inputs are required.
    """
    if len(args) < 2:
        raise ValueError("min requires at least 2 inputs")

    result = args[0]
    for arg in args[1:]:
        if isinstance(result, (pd.Series, pd.DataFrame)) or isinstance(arg, (pd.Series, pd.DataFrame)):
            result = np.minimum(result, arg)
        else:
            result = min(result, arg)

    return result

def multiply(*args, filter=False):
    """
    Multiply all inputs. At least 2 inputs are required. Filter sets the NaN values to 1.
    """
    if len(args) < 2:
        raise ValueError("multiply requires at least 2 inputs")

    result = args[0].copy() if hasattr(args[0], 'copy') else args[0]

    if filter:
        # Replace NaN with 1 before multiplying
        if isinstance(result, (pd.Series, pd.DataFrame)):
            result = result.fillna(1)

    for arg in args[1:]:
        if filter and isinstance(arg, (pd.Series, pd.DataFrame)):
            arg_clean = arg.fillna(1)
            result = result * arg_clean
        else:
            result = result * arg

    return result

def power(x, y):
    """x ^ y"""
    if isinstance(x, (pd.Series, pd.DataFrame)) or isinstance(y, (pd.Series, pd.DataFrame)):
        with np.errstate(divide='ignore', invalid='ignore'):
            result = np.power(x, y)
            return result
    else:
        return np.power(x, y)

def reverse(x):
    """-x"""
    return -x

def sign(x):
    """
    if input = NaN; return NaN
    """
    if isinstance(x, (pd.Series, pd.DataFrame)):
        return np.sign(x)
    else:
        return np.sign(x) if not pd.isna(x) else np.nan

def signed_power(x, y):
    """
    x raised to the power of y such that final result preserves sign of x
    """
    if isinstance(x, (pd.Series, pd.DataFrame)) or isinstance(y, (pd.Series, pd.DataFrame)):
        # Get the sign of x
        x_sign = np.sign(x)
        # Take absolute value, raise to power, then restore sign
        abs_result = np.power(np.abs(x), y)
        result = x_sign * abs_result
        return result
    else:
        if pd.isna(x) or pd.isna(y):
            return np.nan
        x_sign = np.sign(x)
        abs_result = np.power(abs(x), y)
        return x_sign * abs_result

def subtract(x, y, filter=False):
    """
    x-y. If filter = true, filter all input NaN to 0 before subtracting.
    """
    if filter:
        if isinstance(x, (pd.Series, pd.DataFrame)):
            x = x.fillna(0)
        if isinstance(y, (pd.Series, pd.DataFrame)):
            y = y.fillna(0)

    return x - y

def scale(x, scale=1, longscale=1, shortscale=1):
    """
    The operator scales the input to the book size. We can optionally tune the book size by specifying the
    additional parameter 'scale=booksize_value'. We can also scale the long positions and short positions
    to separate scales by specifying additional parameters: longscale=long_booksize and
    shortscale=short_booksize. The default value of each leg of the scale is 0, which means no scaling,
    unless specified otherwise. Scale the alpha so that the sum of abs(x) over all instruments equals 1. To
    scale to a different book size, use Scale(x) * booksize.

    This operator may help reduce outliers.

    Parameters:
    - x: Input alpha values (Series or DataFrame)
    - scale: Overall scaling factor (default 1)
    - longscale: Scaling factor for long positions (default 1)
    - shortscale: Scaling factor for short positions (default 1)

    Examples:
    - scale(returns, scale=4): Scale returns by factor of 4
    - scale(returns, scale=1) + scale(close, scale=20): Combine scaled returns and prices
    - scale(returns, longscale=4, shortscale=3): Different scaling for long vs short positions
    """
    if isinstance(x, (pd.Series, pd.DataFrame)):
        # Create result as copy of input
        result = x.copy().astype(float)

        if isinstance(x, pd.Series):
            # Series case (single stock over time)
            # Apply different scaling to long and short positions
            long_mask = x > 0
            short_mask = x < 0

            # Scale long positions
            if longscale != 1 and long_mask.any():
                result[long_mask] = x[long_mask] * longscale

            # Scale short positions
            if shortscale != 1 and short_mask.any():
                result[short_mask] = x[short_mask] * shortscale

            # Apply overall scale
            if scale != 1:
                result = result * scale

            # Normalize to sum of absolute values = 1 (per the description)
            abs_sum = result.abs().sum()
            if abs_sum > 0:
                result = result / abs_sum

        else:
            # DataFrame case (cross-sectional, multiple stocks)
            # Apply scaling row by row (each time period)
            for i in range(len(x)):
                row_data = x.iloc[i].copy()

                # Apply different scaling to long and short positions
                long_mask = row_data > 0
                short_mask = row_data < 0

                # Scale long positions
                if longscale != 1 and long_mask.any():
                    row_data[long_mask] = row_data[long_mask] * longscale

                # Scale short positions
                if shortscale != 1 and short_mask.any():
                    row_data[short_mask] = row_data[short_mask] * shortscale

                # Apply overall scale
                if scale != 1:
                    row_data = row_data * scale

                # Normalize to sum of absolute values = 1 for this time period
                abs_sum = row_data.abs().sum()
                if abs_sum > 0:
                    row_data = row_data / abs_sum

                result.iloc[i] = row_data

        return result

    else:
        # Scalar case
        scaled_val = x

        # Apply long/short scaling
        if x > 0 and longscale != 1:
            scaled_val = x * longscale
        elif x < 0 and shortscale != 1:
            scaled_val = x * shortscale

        # Apply overall scale
        if scale != 1:
            scaled_val = scaled_val * scale

        return scaled_val

def group_neutralize(x, groups):
    """
    Group neutralization: subtract group mean from each value.

    Parameters:
    - x: Series/DataFrame with values to neutralize
    - groups: Series/DataFrame with group assignments (bucket indices)

    Returns:
    - Series/DataFrame with group-neutralized values
    """
    if isinstance(x, pd.Series) and isinstance(groups, pd.Series):
        # Series case
        result = x.copy()
        for group_id in groups.unique():
            if pd.notna(group_id):
                mask = groups == group_id
                group_mean = x[mask].mean()
                result[mask] = x[mask] - group_mean
        return result

    elif isinstance(x, pd.DataFrame) and isinstance(groups, (pd.Series, pd.DataFrame)):
        # DataFrame case
        result = x.copy()

        if isinstance(groups, pd.Series):
            # Same grouping for all columns
            for group_id in groups.unique():
                if pd.notna(group_id):
                    mask = groups == group_id
                    group_means = x[mask].mean()
                    result[mask] = x[mask] - group_means
        else:
            # Different grouping per column
            for col in x.columns:
                if col in groups.columns:
                    group_col = groups[col]
                    for group_id in group_col.unique():
                        if pd.notna(group_id):
                            mask = group_col == group_id
                            group_mean = x.loc[mask, col].mean()
                            result.loc[mask, col] = x.loc[mask, col] - group_mean

        return result
    else:
        raise ValueError("x and groups must be pandas Series or DataFrame")
