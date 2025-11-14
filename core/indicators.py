import numpy as np
import pandas as pd
import streamlit as st


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
    indicator_type, window = selector
    colname = f"{indicator_type}_{window}"

    # Dont do unnecessary calculations
    if colname in data.columns:
        return data
    
    # Chooses function
    indicator_dict = {
        "SMA": SMA,
        "EMA": EMA,
        "RSI": RSI
    }
    # Calls chosen function

    data = indicator_dict[indicator_type](data, window)
    return data


def add_all_indicators(param_config, params_range, data):
    ''' 
    The indicators step in integer values so 
    we will always be doing less than a thousand this way'''

    progress_text = st.empty()
    for parameter, cfg in param_config.items():
        # find the indicators to be added
        if cfg["type"] == "indicator":
            for indicator_type in cfg["allowed"]: # indicator type looks like 'EMA'
                for i in range(params_range[parameter][0], params_range[parameter][1] + 1):
                    data = fetch_indicator(data, (indicator_type, i)) 
                    percentage = round(((i + 1 - params_range[parameter][0]) / (params_range[parameter][1] + 1- params_range[parameter][0])) * 100, 2)
                    progress_text.write(f"Indicator Progress: {percentage}%")
    progress_text = st.empty()
    return data # set session state






def add_indicators(StrategyClass, current_choice, data_name):
    ''' 
    If we want to change the data we only need to 
    change the st.session_state.df variable 
    make a section on this page to choose/ hold data'''
    df = st.session_state[data_name]
    for parameter, cfg in StrategyClass.param_config.items():
        if cfg['type'] == 'indicator':
            df = fetch_indicator(df, current_choice[parameter]) 
    st.session_state[data_name] = df
