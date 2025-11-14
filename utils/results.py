import streamlit as st
import pandas as pd
import os

from core.strategy_holder import Strategies, strategy_classes

def preliminary_save(data_location, equity_location):
    if (
        st.session_state.get("strategy") is not None
        and getattr(st.session_state.strategy, "equity", None) is not None
        and getattr(st.session_state.strategy, "stats", None) is not None
        ):
        strategy_obj: Strategies = st.session_state.strategy  # type: ignore
        
        # Save run_data - run_data is run name followed by statistics of run
        run_data = strategy_obj.save(st.session_state.last_choice)
        # Store run data to session state
        data_location.append(run_data)

        # Save equity curve as run_data : equity curve
        run_id = len(data_location) - 1
        equity_location[run_id] = strategy_obj.equity

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
        st.sidebar.markdown("### Manage Saved Runs")
        runs_to_delete = st.sidebar.multiselect("Select runs to delete", list(range(len(st.session_state.saved_runs))))

        if st.sidebar.button("Delete Selected Runs"):
            for run_id in sorted(runs_to_delete, reverse=True):
                st.session_state.saved_runs.pop(run_id)
                st.session_state.saved_equities.pop(run_id, None)
            st.success(f"Deleted {len(runs_to_delete)} run(s).")
            st.rerun()

        if st.sidebar.button("Save All to CSV"):
            save_all_results_to_csv()

        if st.sidebar.button("Load Saved Runs"):
            load_all_results_from_csv()
            st.rerun()

def clear_all_saved_runs() -> None:
    """
    Delete all saved runs and equities from session_state and disk.
    Includes confirmation prompt for safety.
    """
    confirm = st.sidebar.checkbox("I understand and want to delete all saved data.")
    if st.sidebar.button("Clear All Saved Runs") and confirm:
        # Clear Streamlit session data
        st.session_state.saved_runs = []
        st.session_state.saved_equities = {}

        # Delete CSV files if they exist
        for file in [RUNS_FILE, EQUITIES_FILE]:
            if os.path.exists(file):
                os.remove(file)

        st.sidebar.success("All saved runs and data have been permanently deleted.")
        st.rerun()


# For saving results
SAVE_DIR = "saved_results"
RUNS_FILE = os.path.join(SAVE_DIR, "runs.csv")
EQUITIES_FILE = os.path.join(SAVE_DIR, "equities.csv")

def save_all_results_to_csv() -> None:
    """
    Save all current results in session_state to CSV files.
    - One CSV for run metadata (st.session_state.saved_runs)
    - One CSV for equity curves (st.session_state.saved_equities)
    """
    os.makedirs(SAVE_DIR, exist_ok=True)

    # --- Save metadata (statistics etc.) ---
    if st.session_state.saved_runs:
        df_runs = pd.DataFrame(st.session_state.saved_runs)
        df_runs.to_csv(RUNS_FILE, index=False)
        st.success(f"Saved {len(df_runs)} runs to {RUNS_FILE}")
    else:
        st.info("No runs to save.")

    # --- Save equity curves ---
    if st.session_state.saved_equities:
        # Pad shorter equity curves with NaN so all have equal length
        max_len = max(len(eq) for eq in st.session_state.saved_equities.values())
        equity_df = pd.DataFrame({
            run_id: pd.Series(eq) for run_id, eq in st.session_state.saved_equities.items()
        })
        equity_df.to_csv(EQUITIES_FILE, index=False)
        st.success(f"Saved equity curves to {EQUITIES_FILE}")
    else:
        st.info("No equity curves to save.")


def load_all_results_from_csv() -> None:
    """
    Load saved results from CSV files into session_state.
    """
    if not os.path.exists(RUNS_FILE):
        st.warning("No saved runs found.")
        return

    # --- Load metadata ---
    df_runs = pd.read_csv(RUNS_FILE)
    st.session_state.saved_runs = df_runs.to_dict(orient="records")
    load_saved_strategies()

    # --- Load equity curves ---
    if os.path.exists(EQUITIES_FILE):
        equity_df = pd.read_csv(EQUITIES_FILE)
        # Convert columns back to numpy arrays, matching original dict form
        st.session_state.saved_equities = {
            int(col): equity_df[col].dropna().to_numpy()
            for col in equity_df.columns
        }

    st.success(f"Loaded {len(st.session_state.saved_runs)} runs from disk.")
    


def load_saved_strategies():
    st.session_state.strategies = []

    for run in st.session_state.saved_runs:
        cls_name = run.get("Strategy")
        cls = strategy_classes.get(cls_name)
        if not cls:
            st.warning(f"Unknown strategy class: {cls_name}")
            continue

        # Extract parameter names back out
        params = {k.replace("param_", ""): v for k, v in run.items() if k.startswith("param_")}

        try:
            strategy_obj = cls(params)
            strategy_obj.stats = {k: v for k, v in run.items() if not k.startswith("param_") and k not in ["Strategy"]}
            st.session_state.strategies.append(strategy_obj)
        except Exception as e:
            st.error(f"Failed to load strategy {cls_name}: {e}")


def explode_indicator_strings(df):
    """
    Find any object column that looks like 'EMA, 12'
    and split it into <col>_type and <col>_window.
    """
    df = df.copy()

    for col in df.columns:
        if df[col].dtype == object:
            # Take a sample non-null value
            sample = df[col].dropna().astype(str).iloc[0]
            # Heuristic: contains a comma
            if "," in sample:
                parts = df[col].astype(str).str.split(",", n=1, expand=True)
                df[f"{col}_type"] = parts[0].str.strip()
                df[f"{col}_window"] = pd.to_numeric(parts[1].str.strip(), errors="coerce")

    return df

def get_results_df(Strategy, data_name):
    data_key = "run_name_" + Strategy.name + data_name
    if data_key not in st.session_state or not st.session_state[data_key]:
        return None
    
    return pd.DataFrame(st.session_state[data_key])