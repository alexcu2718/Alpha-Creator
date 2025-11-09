import streamlit as st
import pandas as pd
from core.strategy_holder import Strategies

def choose_plot_columns(indicators: list[tuple[str, int]]) -> None:
    """
    Display the main price chart with selected indicators.

    This function:
      - Plots the closing price and any added indicators (e.g., SMA, EMA)
      - Displays RSI indicators on a separate subchart if present

    Args:
        indicators (list[tuple[str, int]]):
            list of indicators, looks like (indicator_type, window_size)
    """
    if st.session_state.df is None:
        return 
    st.subheader("Price Graph")
    # Initialises two lists of column names to plot
    normal_cols = ["Close"]
    rsi_cols = []
    
    for item in indicators:
        # If indicator it RSI it adds the column name to the second list
        if item[0] == "RSI":
            rsi_cols.append(f"{item[0]}_{item[1]}") 
        else: # If not RSI, it adds column name to normal columns
            normal_cols.append(f"{item[0]}_{item[1]}")

    st.line_chart(st.session_state.df[normal_cols])
    # Plots any RSI indicators on a separate graph
    if rsi_cols:
        st.subheader("RSI Graph")
        st.line_chart(st.session_state.df[rsi_cols])



def display_current_strategy(strategy: Strategies | None) -> None:
    """
    Display the equity curve and performance statistics for the current strategy.

    If a strategy instance is provided, this function:
      - Plots its equity curve
      - Displays its performance statistics below the chart
    Args:
        strategy (Strategies) subclass of Strategies, contains:
            equity (np.ndarray) equity curve of backtest
            stats (dict[str, float]): Computed metrics  
    """
    if strategy is None:
        return

    # Explicit guards for Pylance and correctness
    if strategy.equity is None or strategy.stats is None:
        st.info("Run a strategy test to see the equity curve and stats.")
        return
    
    st.subheader("Equity Curve")
    # Plot equity chart
    st.line_chart(strategy.equity - 1)
    for key, value in strategy.stats.items():
            st.write(f"{key}: {value}")

def choose_results_to_plot() -> None:
    """
    Displays comparison of saved runs.

    Allows user to select from currently saved runs,
    Plots each selected run on the same graph
    """
    if st.session_state.saved_runs:
        selected_runs = st.multiselect("Select runs to plot", st.session_state.saved_equities.keys())

        if selected_runs:
            # Build a DataFrame with each column = one equity curve
            df_equities = pd.DataFrame({run_id: st.session_state.saved_equities[run_id] for run_id in selected_runs})
            
            # Plots profit instead
            df_equities = df_equities - 1

            # Plot all curves together
            st.line_chart(df_equities)
        else:
            st.info("Select one or more runs to view their equity curves.")

