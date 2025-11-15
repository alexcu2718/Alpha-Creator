import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from core.backtester import simple_backtest
from utils.session import init_session_state, run_strategy, hold_results, compare_strategies, test_stability
from utils.results import results_management
from ui.sidebar import select_data, select_indicator, remove_indicator, select_strategy, test_strategy_button, permanently_delete
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
StrategyClass, params = select_strategy()
if test_strategy_button():
    st.session_state.strategy = run_strategy(StrategyClass, params, simple_backtest, st.session_state.df, st.session_state.saved_runs, st.session_state.saved_equities)
display_current_strategy(st.session_state.strategy)

#---RESULTS---
results_management(st.session_state.strategy)
hold_results(st.session_state.saved_runs)
choose_results_to_plot()
permanently_delete()

#---STRATEGY COMPARISON---
compare_strategies()
test_stability()




#---QUICK ADDITIONS---

# Remove all non-permanent strategies

# Page Break before comparing strategies



# Big adds

# Combine strategies seems like the most fun option.

# So far, added ability to compare similarities between strategy inputs

# Need to do so for strategy outputs too, maybe this is just percentage profit. Lets say this is a combo of that and sharpe ratio

# Could add section to plot different run types, maybe plot top 3 runs for sharpe ratio, or top 3 for profit





# Change how indicators are chosen for individual strategies. 
# You should be able to choose specific compatible indicators and thats it 
# The indicators should save to the dataframe whenever they are chosen, 
# ie for viewing them against stock data, or when testing strategies

# When we choose a strategy it should bring up place to select each indicator, ie select indicator type, then has allowed types


# Confusing thinker

# The metric for measuring inputs is generally just bad.
# Maybe could use exponential functions, this means that when window the margin changes by a lot, then the L value will be small regardless,



# Bug fixes:

# Need to round things better - margin currently when -0.00 goes to -3.49e-18 or something similar