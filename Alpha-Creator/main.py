import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from core.backtester import simple_backtest
from utils.session import init_session_state, run_strategy, hold_results
from utils.results import results_management
from ui.sidebar import select_data, select_indicator, remove_indicator, choose_strategy, test_strategy_button
from ui.plots import choose_plot_columns, display_current_strategy, choose_results_to_plot

#---INITIALISE STATE---
init_session_state()

#---SELECT DATA---
select_data()

#---GET/REMOVE INDICATORS---
select_indicator()
choose_plot_columns(st.session_state.indicators)
remove_indicator()

#---STRATEGY SELECTION AND RUNNING---
StrategyClass, params = choose_strategy()
if test_strategy_button():
    st.session_state.strategy = run_strategy(StrategyClass, params, simple_backtest)
display_current_strategy(st.session_state.strategy)

#---RESULTS---
results_management(st.session_state.strategy)
hold_results()
choose_results_to_plot()






# Future Goals

# Results manager

# Ability to store results long term, put them in csv and retrieve them when loaded, we should be able to delete them using the manager.

# Want to be able to delete all results with a warning

# Combine strategies seems like the most fun option.

# Goal for tomorrow. Refactor main script so that it is just a pipeline not messy code!!!!

 # Could add section to plot different run types, maybe plot top 3 runs for sharpe ratio, or top 3 for profit