import numpy as np
import pandas as pd
from core.graphsandstats import get_stats
from typing import Optional, Dict, Any, Callable
import datetime


class Strategies:
    '''
    Holds the shared functions for each strategy'''
    name = "Base Strategy"
    param_config = {}

    def __init__(self, params):
        self.params: Dict[str, Any] = params
        self.signals: Optional[np.ndarray] = None
        self.stats: Optional[Dict[str, float]] = None
        self.equity: Optional[np.ndarray] = None
        self.trade_fee: float = params.get("cost_per_trade", 0.5)

    def generate_signals(self, data: pd.DataFrame):
        '''Specific to chosen strategy'''
        raise NotImplementedError
    
    def save(self, cryptodata: tuple[str, str, str]) -> Dict[str, Any]:
        '''Return a dictionary safe for DataFrame conversion.
        '''
        if self.equity is None or self.stats is None:
            raise ValueError("Backtest and stats must be computed before saving.")

        def format_value(v):
            # Always return a simple string
            if isinstance(v, (list, tuple)):
                return ", ".join(map(str, v))
            return str(v)
        
        formatted_params = {f"{k}": format_value(v) for k, v in self.params.items()}

        formatted_stats = {
            k: float(v) if isinstance(v, (int, float, np.number)) else str(v)
            for k, v in self.stats.items()
        }
        asset, period, interval = cryptodata
        
        return {
            "Asset": asset,
            "Period": period,
            "Interval": interval,
            "Strategy": self.__class__.__name__,
            **formatted_stats,
            **formatted_params,
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        }

    def backtest(self, data: pd.DataFrame, backtestfunc: Callable):
        '''
        If signals have been generated it uses the given backtesting method to get an equity curve for the strategy
        Args:
            data:  (pandas dataframe) contains historical price data
            backtestfunc: (function) name of back testing function from backtester.py
        '''
        if self.signals is None:
            raise ValueError("No signals have been generated yet")
        
        self.equity = backtestfunc(data["Close"], self.signals, self.trade_fee)
        return self.equity

    def compute_stats(self) -> Dict[str, Any]:
        '''
        Checks if the equity has been calculated for the strategy
        Obtains the statistics of the strategy'''
        if self.equity is None:
            raise ValueError("Strategy must be tested first")
        self.stats = get_stats(self.equity)
        return self.stats

    def __repr__(self):
        return f"{self.name}({self.params})"
    





class SimpleMeanReversion(Strategies):
    """
    A basic mean reversion trading strategy.

    This strategy compares the current price to a moving average indicator 
    (e.g. SMA, EMA) and generates buy or sell signals when the deviation 
    exceeds a specified margin threshold.

    Attributes:
        name (str): The display name for the strategy.
        param_config (dict): Configuration schema defining the required parameters.

    Parameters expected in `self.params`:
        - indicator (tuple[str, int]): The type and window length of the indicator 
          (e.g. ("SMA", 20)).
        - margin (float): The percentage deviation threshold that triggers trades.
        - cost_per_trade (float): The assumed transaction cost per trade (not used directly here).

    Inherits from:
        Strategies: The base strategy class providing core structure 
        for signal generation, backtesting, and statistics.
    """
    name = "Simple Mean Reversion"

    param_config = {
        "indicator": {"type": "indicator", "label": "Indicator", "allowed": ["SMA", "EMA"], "metric": "discrete"},
        "margin": {"type": "float", "label": "Margin", "value": 0.05, "step": 0.01, "metric": "exponential"},
        "cost_per_trade": {"type": "float", "label": "Cost Per Trade %", "value": 0.5, "step": 0.1, "metric": "none"},
    }
    
    def generate_signals(self, data: pd.DataFrame) -> np.ndarray:
        """
        Generate trading signals based on deviation from a moving average indicator.

        Args:
            df (pd.DataFrame): 
                DataFrame contains 'Close' and the chosen indicator column 
                (e.g., 'SMA_20' or 'EMA_50').

        Returns:
            np.ndarray: 
                Array of trading signals where:
                    1 = buy, -1 = sell, 0 = no action.
        """
        indicator = self.params["indicator"]
        kind, length = indicator
        margin = self.params["margin"]
        if (not indicator) or (margin is None):
            return np.array([])
        prices = data["Close"].to_numpy()
        average = data[f"{kind}_{length}"].to_numpy()
        signals = np.zeros(len(data), dtype=int)

        for i in range(length, len(prices)):
            if prices[i] > average[i] * (1 + margin):
                signals[i] = 1
            elif prices[i] < average[i] * (1 - margin):
                signals[i] = -1

        self.signals = signals

        return self.signals
    
class BasicMomentum(Strategies):
    """
    A classic moving average crossover strategy.

    This strategy compares a short-term and long-term moving average indicator 
    (e.g., SMA or EMA) and generates buy/sell signals when the short-term 
    average diverges from the long-term average by a specified margin.

    Attributes:
        name (str): Display name for the strategy.
        param_config (dict): Configuration schema defining the strategy parameters.

    Expected parameters (self.params):
        - Short_MA (tuple[str, int]): Type and window of short moving average.
        - Long_MA (tuple[str, int]): Type and window of long moving average.
        - margin (float): Percentage threshold for deviation.
        - cost_per_trade (float): Transaction cost per trade.

    Inherits from:
        Strategies
    """
    name = "Moving Average Crossover"

    param_config = {
        "Short_MA": {"type": "indicator", "label": "Short Indicator", "allowed": ["SMA", "EMA"], "metric": "discrete"},
        "Long_MA": {"type": "indicator", "label": "Long Indicator", "allowed": ["SMA", "EMA"], "metric": "discrete"},
        "margin": {"type": "float", "label": "Margin", "value": 0.05, "step": 0.01, "metric": "exponential"},
        "cost_per_trade": {"type": "float", "label": "Cost Per Trade %", "value": 0.5, "step": 0.1, "metric": "none"},
    }

    def generate_signals(self, data):
        """
        Generate buy/sell signals based on crossover between two moving averages.

        Logic:
            - +1 (buy)  if short_MA > long_MA × (1 + margin)
            - -1 (sell) if short_MA < long_MA × (1 - margin)
            -  0 (hold) otherwise

        Args:
            df (pd.DataFrame): DataFrame containing the short and long indicator columns.

        Returns:
            np.ndarray: Array of integer signals (1 = buy, -1 = sell, 0 = hold).
        """
        short = self.params["Short_MA"]
        long = self.params["Long_MA"] 
        margin = self.params["margin"]
        if (not short) or (not long) or (margin is None):
            return
        
        short_data = data[f"{short[0]}_{short[1]}"].to_numpy()
        long_data = data[f"{long[0]}_{long[1]}"].to_numpy()
        signals = np.zeros(len(data), dtype=int)

        for i in range(long[1], len(data)):
            if short_data[i] > long_data[i] * (1 + margin):
                signals[i] = 1
            elif short_data[i] < long_data[i] * (1 - margin):
                signals[i] = -1

        self.signals = signals
        return self.signals
        


class BasicRSI(Strategies):
    """
    A simple RSI (Relative Strength Index) threshold strategy.

    Generates buy/sell signals based on RSI values:
      - Buy when RSI < lower threshold
      - Sell when RSI > upper threshold

    Attributes:
        name (str): Display name for the strategy.
        param_config (dict): Configuration schema defining parameters.

    Expected parameters (self.params):
        - indicator (tuple[str, int]): RSI indicator and its window size.
        - margin (float): RSI threshold (0–0.5) used for upper/lower bounds.
        - cost_per_trade (float): Transaction cost per trade.

    Inherits from:
        Strategies
    """
    name = "Basic RSI"

    param_config = {
        "indicator": {"type": "indicator", "label": "Indicator", "allowed": ["RSI"],  "metric": "discrete"},
        "margin": {"type": "float", "label": "Margin", "value": 0.25, "step": 0.01, "metric": "exponential"},
        "cost_per_trade": {"type": "float", "label": "Cost Per Trade %", "value": 0.5, "step": 0.1, "metric": "none"},
    }
    
    def generate_signals(self, data):
        """
        Generate buy/sell signals based on RSI thresholds.

        Logic:
            - +1 (buy)  if RSI < 100 × margin
            - -1 (sell) if RSI > 100 - (100 × margin)
            -  0 (hold) otherwise

        Args:
            df (pd.DataFrame): DataFrame containing the RSI indicator column.

        Returns:
            np.ndarray: Array of integer signals (1 = buy, -1 = sell, 0 = hold).
        """
        signals = np.zeros(len(data), dtype=int)
        indicator = self.params["indicator"]
        RSI_data = data[f"{indicator[0]}_{indicator[1]}"]

        margin = self.params["margin"] * 100
        
        for i in range(indicator[1], len(data)):
            if RSI_data[i] < margin:
                signals[i] = 1
            elif RSI_data[i] > 100 - margin:
                signals[i] = - 1

        self.signals = signals

        return self.signals
    
class Bollinger(Strategies):
    """
    A Bollinger Bands-based mean reversion strategy.

    This strategy uses price deviation from Bollinger Bands to generate signals:
      - Buy when price falls below the lower band × (1 - margin)
      - Sell when price exceeds the upper band × (1 + margin)

    Attributes:
        name (str): Display name for the strategy.
        param_config (dict): Configuration schema defining parameters.

    Expected parameters (self.params):
        - indicator (tuple[str, int]): Moving average used for the band centre.
        - factor (float): Multiplier for standard deviation width.
        - margin (float): Additional percentage buffer.
        - cost_per_trade (float): Transaction cost per trade.

    Inherits from:
        Strategies
    """
    name = "Bollinger"
    param_config = {
        "indicator": {"type": "indicator", "label": "Indicator", "allowed": ["SMA", "EMA"], "metric": "discrete"},
        "factor": {"type": "float", "label": "Factor", "value": 0.5, "step": 0.1, "metric": "exponential"},
        "margin": {"type": "float", "label": "Margin", "value": 0.05, "step": 0.01, "metric": "exponential"},
        "cost_per_trade": {"type": "float", "label": "Cost Per Trade %", "value": 0.5, "step": 0.1, "metric": "none"},
    }

    def generate_signals(self, data):
        """
        Generate buy/sell signals based on Bollinger Band breakouts.

        Args:
            df (pd.DataFrame): DataFrame containing 'Close' and the chosen indicator column.

        Returns:
            np.ndarray: Array of integer signals (1 = buy, -1 = sell, 0 = hold).
        """
        indicator = self.params["indicator"]
        kind, length = indicator
        margin = self.params["margin"]
        factor = self.params["factor"]
        if (not indicator) or (margin is None):
            return 
        prices = data["Close"].to_numpy()
        std_windows = data["Close"].rolling(length).std().to_numpy()
        average = data[f"{kind}_{length}"].to_numpy()
        signals = np.zeros(len(data), dtype=int)


        for i in range(length, len(prices)):
            if prices[i] > (average[i] + factor * std_windows[i]) * (1 + margin):
                signals[i] = 1
            elif prices[i] < (average[i] - factor * std_windows[i]) * (1 - margin):
                signals[i] = -1

        self.signals = signals

        return self.signals
    

strategy_classes = {
    "SimpleMeanReversion": SimpleMeanReversion,
    "BasicMomentum": BasicMomentum,
    "BasicRSI": BasicRSI,
    "Bollinger": Bollinger,
}