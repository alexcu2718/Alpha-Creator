import pandas as pd
import yfinance as yf
import streamlit as st


@st.cache_data(show_spinner=False)
def get_crypto_data(
    symbol: str = "BTC-USD",
    period: str = "365d",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Fetch market data (crypto or stock) using yfinance and return a clean DataFrame.

    Args:
        symbol: Ticker to fetch, e.g. "BTC-USD", "AAPL"
        period: Lookback window, e.g. "30d", "180d", "365d"
        interval: Bar size, e.g. "1d", "1h", "5m"

    Returns:
        pd.DataFrame with datetime index and OHLCV columns.
        Returns an empty DataFrame (and shows a message) if download fails.
    """
    try:
        data = yf.download(
            tickers=symbol,
            interval=interval,
            period=period,
            auto_adjust=True,
            progress=False,
        )
    except Exception as e:
        st.error(f"Failed to download data for {symbol}: {e}")
        return pd.DataFrame()

    # Handle no data / bad response
    if data is None or data.empty:
        st.warning(
            f"No data returned for {symbol} with period={period}, interval={interval}. "
            "Try a shorter period or coarser interval."
        )
        return pd.DataFrame()

    # Flatten MultiIndex columns if present (yfinance sometimes does this)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Ensure datetime index without timezone (Streamlit friendly)
    data.index = pd.to_datetime(data.index)
    if getattr(data.index, "tz", None) is not None:
        data.index = data.index.tz_localize(None)

    return data


