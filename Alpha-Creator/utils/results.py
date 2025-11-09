import streamlit as st
from core.strategy_holder import Strategies

def results_management(strategy: Strategies | None) -> None:
    """
    Manage saving, displaying, and deleting strategy backtest results.

    This function provides an interface within Streamlit to:
      - Save the current strategy's statistics and equity curve to session state
      - Display saved runs for review
      - Delete selected runs from storage

    When the 'Save Results' button is pressed, the current strategy's results 
    are appended to `st.session_state.saved_runs` (for summary statistics)
    and `st.session_state.saved_equities` (for equity curves).

    Args:
        strategy (Strategies | None): 
            The active strategy instance containing computed `equity` and `stats`.
            If None or incomplete, the interface does not display saving options.

    """
    if (
        st.session_state.get("strategy") is not None
        and getattr(st.session_state.strategy, "equity", None) is not None
        and getattr(st.session_state.strategy, "stats", None) is not None
        ):
        strategy_obj: Strategies = st.session_state.strategy  # type: ignore
        if st.button("Save Results"):
            # Save run_data - run_data is run name followed by statistics of run
            run_data = strategy_obj.save(st.session_state.last_choice)
            # Store run data to session state
            st.session_state.saved_runs.append(run_data)

            # Save equity curve as run_data : equity curve
            run_id = len(st.session_state.saved_runs) - 1
            st.session_state.saved_equities[run_id] = strategy_obj.equity
            st.success("Saved Successfully!")
        
        st.markdown("### Manage Saved Runs")
        runs_to_delete = st.multiselect("Select runs to delete", list(range(len(st.session_state.saved_runs))))

        if st.button("Delete Selected Runs"):
            for run_id in sorted(runs_to_delete, reverse=True):
                st.session_state.saved_runs.pop(run_id)
                st.session_state.saved_equities.pop(run_id, None)
            st.success(f"Deleted {len(runs_to_delete)} run(s).")
            st.rerun()