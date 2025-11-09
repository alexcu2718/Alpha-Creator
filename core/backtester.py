import numpy as np
import pandas as pd

def simple_backtest(prices: pd.Series, signals: np.ndarray, trade_fee: float=0.5) -> np.ndarray:
    '''
    Takes in signals and prices, simulates buying and selling the stock with all of the funds available at any given time. Only long positions are allowed
    Args:
        prices: (pandas series) closing price of asset 
        signals: (numpy array) contains 1, 0, -1, depending on whether to buy stock, do nothing, or sell
    Returns:
        (numpy array) equity curve produced by the given signals
    '''
    signals = np.concatenate(([0], signals[:-1]))
    holding = False

    # Get returns on prices
    returns = np.diff(prices) / prices[:-1]
    change = []

    # Account for trading fees
    fees = np.ones(len(signals) - 1)
    decrease = 1 - (trade_fee * 0.01)
    
    for i in range(len(signals) - 1):
        if signals[i] == 1:
            if not holding:
                fees[i] = decrease
            holding = True
        elif signals[i] == -1:
            if holding:
                fees[i] = decrease
            holding = False

        if holding:
            change.append(returns[i])
        else: 
            change.append(0)
    
    change = np.array(change)
    equity = ((1 + change) * fees).cumprod()
    return equity