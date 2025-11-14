import streamlit as st
import pandas as pd

from ui.results_ui import choose_results
from utils.results import explode_indicator_strings
from core.graphsandstats import show_heatmap, heatmap_selector



st.header("Results Analysis")


#---CHOOSE DATAFRAME
choose_results()
df = st.session_state.current_optimiser_results


#---PLOTTING HEATMAP---
df = explode_indicator_strings(df)
if isinstance(df, pd.DataFrame) and not df.empty:
    st.dataframe(df)
    heatmap_selector(df, show_heatmap)