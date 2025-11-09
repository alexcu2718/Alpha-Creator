import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import time
from io import StringIO
import json
import streamlit as st
from typing import Any, Optional

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
    return round(np.mean(abs(trades)), 2)




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