import streamlit as st
import pandas as pd
from ui.sidebar import strategy_classes, select_data
from utils.session import init_optimiser_session_state

from core.global_optimiser import run_global_sim, choose_strategy


#---PIPELINE---
init_optimiser_session_state()
st.write("We assume a fixed cost per trade of 0.5%")


#---SELECT STRATEGY, PARAMETER RANGE AND DATA---
Strategy, params_range = choose_strategy()
select_data(specific_location=True)


#---RUN GLOBAL OPTIMISER---
run_global_sim(Strategy, st.session_state["name"], params_range) 






















#---BUGS---
# fix global percentage.
# Fix percentages in general





#---Changes---

# Make a column thats profit - change from just holding stock for whole time


# Make it so we can filter the results
