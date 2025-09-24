import pandas as pd
import numpy as np


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


# Comparison operators
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