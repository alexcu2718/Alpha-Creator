import pandas as pd
import yfinance as yf
import streamlit as st


@st.cache_data(show_spinner=False)
def get_crypto_data(symbol: str="BTC-USD", period: str="365d", interval: str='1d') -> pd.DataFrame:
    '''
    Fetches cryptocurrency data and stores it in a pandas dataframe.
    Args:
        symbol: string,the ticker to be used
        period: string, number of days followed by d
        interval: string, period of time between fetching of price
    Returns:
        data: pandas DataFrame of historical price data, has a timestap and OHLCV'''
    data = yf.download(
        tickers=symbol,
        interval=interval,
        period=period,
        auto_adjust=True
    )
    data.columns = data.columns.get_level_values(0)
    data.index = pd.to_datetime(data.index)

    # Remove timezone info if exists (Streamlit hates tz-aware indexes)
    data.index = data.index.tz_localize(None)
    return data



