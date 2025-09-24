import pandas as pd
import numpy as np


def Abs(x):
    return x.abs()


def Sqrt(x):
    """Safe square root function that handles negative values"""
    if isinstance(x, pd.Series):
        return x.clip(lower=0).apply(np.sqrt)
    else:
        return x.clip(lower=0).apply(np.sqrt)


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