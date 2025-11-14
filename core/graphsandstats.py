from math import exp, inf
import numpy as np
import streamlit as st
from typing import Any
from math import exp
import altair as alt
import pandas as pd


# STATISTICS
def sharpe_ratio(equity: np.ndarray, risk_free_return: float=0) -> float:
    '''Args:
        equity (numpy array) of profit and loss for a given test of a strategy
        risk_free_return (float) risk free return to compare against
    Returns:
        sharpe_ratio (float)'''
    returns = np.diff(equity)
    standard_dev = np.std(returns)

    if standard_dev == 0:
        return 0.0
    
    return np.sqrt(len(returns)) * (np.mean(returns) - risk_free_return) / standard_dev


def get_trades(equity: np.ndarray) -> np.ndarray:
    '''
    Extracts individual trade returns from an equity curve.
    Args:
        equity: Pandas Series of cumulative equity or portfolio values
            over time.
    Returns:
        A NumPy array of trade returns (as floats), where each element
        represents the percentage change of one completed trade.
        Returns an empty array if no trades are detected.
    '''
    in_trade = False
    start_trade = equity[0]
    trades = []
    for i in range(1, len(equity)):
        if abs(equity[i] - equity[i - 1]) < 1e-12:
            if in_trade:
                # Get result of trade:
                trade_result = equity[i] / start_trade - 1
                trades.append(trade_result)
                in_trade = False


        else:
            if not in_trade:
                start_trade = equity[i - 1]
                in_trade = True

    if in_trade:
        trade_result = equity[-1] / start_trade - 1
        trades.append(trade_result)

    return np.array(trades)

def max_changes(trades: np.ndarray) -> tuple[float, float]:
    '''
    Computes the largest win and loss from an individual trade in terms of percentage of money invested
    Args:
        trades numpy array of the results of different trades
    Returns:
        Biggest Loss: float 
        Biggest Gain: float'''
    if len(trades) == 0:
        return 0.0, 0.0
    return round(min(trades), 2), round(max(trades), 2)
    

def win_rate(trades: np.ndarray) -> float:
    '''
    Calculates the percentage of times a trade is profitable
    Args:
        trades numpy array of the results of different trades   
    Returns:
        win_rate (float) proportion of trades that are positive'''
    if len(trades) == 0:
        return 0.0
    return round(np.sum(trades > 0) / len(trades), 2)


def avg_trade_size(trades: np.ndarray) -> float:
    '''Calculates the average equity change of each trade
    Args:
        trades numpy array of the results of different trades
    Returns:
        Float: average change in equity from each trade (absolute value)'''
    return round(np.mean(abs(trades)), 2) # type: ignore




def get_stats(equity: np.ndarray) -> dict[str, Any]:
    '''
    Takes in the equity from a given strategy, gets the statistics of the equity curve
    Args:
        trades numpy array of the results of different trades
    Returns:
        Dictionary of statistics for a given equity curve.'''
    trades = get_trades(equity)
    # Remove this line from each function
    min_change, max_change = max_changes(trades)
    avg_size = avg_trade_size(trades)
    number_of_trades = len(trades)
    winrate = win_rate(trades)
    sharpe = sharpe_ratio(equity)
    return {
        "Profit %": round((equity[-1] - 1) * 100, 2),
        "Biggest Win %": round(max_change * 100, 2), 
        "Biggest Loss %": round(min_change * 100, 2), 
        "Average Trade Size %": round(avg_size * 100, 2), 
        "Number of Trades": round(number_of_trades, 2), 
        "Win Rate %": round(winrate * 100, 2), 
        "Sharpe Ratio": round(sharpe, 2)
        }

def parse_indicator(value) -> tuple[str, int] | str:
    """
    Convert 'SMA, 20' → (SMA, 20) if applicable.
    Changes string of an indicator back into a tuple.
    """
    if isinstance(value, str) and "," in value:
        parts = [x.strip() for x in value.split(",")]
        if len(parts) == 2:
            name = parts[0]
            try:
                window = int(parts[1])
            except ValueError:
                return value  # keep as string if can't parse
            return (name, window)
    return value


def compare_strategy_inputs(s1: dict, s2 : dict, parameters: dict) -> float:
    """

    Compute a similarity distance between two strategy instances. Currently only works for SimpleMeanReversion
    """
    if (s1['Strategy'] != s2['Strategy'] 
        or s1["Asset"] != s2["Asset"]
        or s1["Period"] != s2["Period"]
        or s1["Interval"] != s2["Interval"]
        or s1["cost_per_trade"] != s2["cost_per_trade"]):
        return inf
    dist = 0

    # Features in param_config but not useful in the metric
    

    for key in parameters:
        y = 0
        if parameters[key]['metric'] == "discrete":
            type1, period1 = parse_indicator(s1[key])
            type2, period2 = parse_indicator(s2[key])
            y = 0.5 if type1 != type2 else 0
            x = abs(float(period1) - float(period2))
            z = round(abs(exp(-x) - 1), 2) / 2
            a = y + z

        elif parameters[key]['metric'] == "exponential":
            x = abs(float(s1[key]) - float(s2[key]))
            y = round(abs(exp(-x) - 1), 2)

        dist += y

    # Normalise distance function
    n = max(len(parameters), 1)
    dist = dist / n
    return dist



def compare_strategy_results(s1, s2, parameters):
    return round(abs(s1["Profit %"] - s2["Profit %"]) / 100, 3)


def get_current_ratio(inputs_metric, results_metric):

    if inputs_metric - 0 < 1e-12:
        ratio = 0.000
    else:
        ratio = round(results_metric / inputs_metric, 3)
    return ratio




#---GRAPHS---
def show_heatmap(df, x_param, y_param, metric):
    chart = (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=alt.X(f"{x_param}:Q", bin=True),
            y=alt.Y(f"{y_param}:Q", bin=True),
            color=alt.Color(f"{metric}:Q", scale=alt.Scale(scheme="viridis")),
            tooltip=[x_param, y_param, metric]
        )
    )
    st.altair_chart(chart, use_container_width=True)


def heatmap_selector(df, plot_fn):
    """
    Sidebar UI component for selecting heatmap parameters.
    
    Parameters:
        df : DataFrame (after exploding indicator strings)
        plot_fn : a function like show_heatmap(df, x, y, metric)
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.info("No optimiser results available yet.")
        return

    # -------- Select valid parameter columns --------
    # numeric parameter columns
    numeric_params = [
        col for col in df.columns
        if (
            ("window" in col) or               # indicator window columns
            ("margin" in col) or               # margin-like params
            ("factor" in col) or               # factor params
            ("threshold" in col) or            # threshold params
            (col.startswith("param_") and pd.api.types.is_numeric_dtype(df[col]))
        )
    ]

    # -------- Select valid metric columns --------
    numeric_metrics = [
        col for col in df.columns
        if (
            pd.api.types.is_numeric_dtype(df[col]) and        # numeric
            not any(k in col for k in ["window", "margin", "factor", "param_"])
        )
    ]

    with st.sidebar.expander("Heatmap Options"):
        st.write("Select parameters to visualise")

        if not numeric_params:
            st.warning("No numeric parameter columns found.")
            return
        
        if not numeric_metrics:
            st.warning("No metric columns found.")
            return

        x_col = st.selectbox("X Axis (parameter)", numeric_params, key="heat_x")
        y_col = st.selectbox("Y Axis (parameter)", numeric_params, key="heat_y")
        metric_col = st.selectbox("Metric (colour)", numeric_metrics, key="heat_metric")
        
        plot_button = st.button("Plot Heatmap", key="heat_button")

    if plot_button:
        if x_col == y_col:
            st.warning("X and Y must be different parameters.")
            return
        
        plot_fn(df, x_col, y_col, metric_col)

