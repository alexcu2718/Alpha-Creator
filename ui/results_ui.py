import streamlit as st
import pandas as pd

from ui.sidebar import data_select_box
from core.strategy_holder import strategy_classes
from utils.results import get_results_df




def choose_results():
    '''
    Select data and strategy
    '''
    with st.sidebar.expander("Select Data"):
        strategy_type = st.selectbox("Strategy", ["None"] + list(strategy_classes.keys()), key='results_strategy')
        crypto, period, interval = data_select_box(key="Results_Selection")

        if st.button("Fetch Results", key="fetch_results"):
            # Use correct data_name
            data_name = f"{crypto}_{interval}_{period}"
            
            st.session_state.current_strategy = strategy_type
            st.session_state.current_data_name = data_name
    # Load results
    if (
        "current_strategy" in st.session_state 
        and st.session_state.current_strategy != "None"
        and "current_data_name" in st.session_state
    ):
        StrategyClass = strategy_classes[st.session_state.current_strategy]
        data_name = st.session_state.current_data_name
        df = get_results_df(StrategyClass, data_name)
        if df is None:
            st.warning("No results found for this selection.")
            st.session_state.current_optimiser_results = pd.DataFrame()
        else:
            st.session_state.current_optimiser_results = df