import numpy as np
import pandas as pd


def SMA(data: pd.DataFrame, window: int) -> pd.DataFrame:
    '''
    Calculates Simple Moving Average stores it in the dataframe with name "SMA_window
    Args:
        df: (pandas dataframe) price data
        window: (integer) number of price checks to average over
    Returns:
        data: (pandas dataframe) containing the added simple moving average indicator with the chosen window size
    '''
    data[f"SMA_{window}"] = data["Close"].shift(1).rolling(window).mean()
    return data

def EMA(data: pd.DataFrame, window: int) -> pd.DataFrame:
    '''
    Calculates Exponential Moving Average stores it in the dataframe with name "EMA_window
    Args:
        df: (pandas dataframe) price data
        window: (integer) number of price checks to average over
    Returns:
        data: (pandas dataframe) containing the added exponential moving average indicator with the chosen window size
    '''
    k = 2 / (window + 1)
    col = f"EMA_{window}"

    # Initialize column
    data[col] = np.nan

    # Get first value
    data.loc[data.index[window-1], col] = data["Close"].iloc[:window].mean()

    # Compute EMA recursively
    for i in range(window, len(data)):
        data.loc[data.index[i], col] = (
            k * data["Close"].iloc[i]
            + (1 - k) * data[col].iloc[i - 1]
        )

    return data

def RSI(data: pd.DataFrame, window: int) -> pd.DataFrame:
    '''
    Calculates Relative strength index, stores it in the dataframe with name "RSI_window
    Args:
        df: (pandas dataframe) price data
        window: (integer) number of price checks to calculate indicator over
    Returns:
        data: (pandas dataframe) containing the added relative strength index indicator with the chosen window size
    '''
    col = f"RSI_{window}"
    data[col] = np.nan
    differences = np.diff(data["Close"].iloc[:window])
    for i in range(window, len(data)):
        differences = differences[1:]
        new_diff = data["Close"].iloc[i] - data["Close"].iloc[i - 1]
        differences = np.append(differences, new_diff)
        avg_gain = np.mean(differences[differences >= 0])
        avg_loss = abs(np.mean(differences[differences < 0]))
        if avg_loss == 0: rs = 0
        else:
            rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        data.loc[data.index[i], col] = rsi

    return data

def fetch_indicator(data: pd.DataFrame, selector: tuple[str, int]) -> pd.DataFrame:
    '''
    Chooses which indicator to add and calls that function
    Args:
        data: (pandas dataframe)  price data
        selector: tuple(string, int), contains name of indicator and window size
    Returns: 
        pandas dataframe with row added containing the new indicator
    '''
    # Chooses function
    funct_dict = {
        "SMA": SMA,
        "EMA": EMA,
        "RSI": RSI
    }
    # Calls chosen function
    data = funct_dict[selector[0]](data, selector[1])
    return data

