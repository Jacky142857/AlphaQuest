import pandas as pd
import numpy as np

# Handle scipy import with fallback
try:
    from scipy.stats import norm, cauchy, uniform
    SCIPY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: SciPy not available: {e}")
    SCIPY_AVAILABLE = False
    # Create fallback functions
    class MockDistribution:
        @staticmethod
        def ppf(x):
            return np.array(x)  # Simple fallback
    norm = cauchy = uniform = MockDistribution()


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