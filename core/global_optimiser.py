import streamlit as st
import random
from core.indicators import add_all_indicators
from utils.session import run_strategy, hold_results
from core.backtester import simple_backtest
from core.strategy_holder import strategy_classes



def run_global_sim(Strategy, data_name, params_range):
    st.sidebar.markdown("---")
    st.sidebar.header("Test Parameter Range:")
    #st.write(st.session_state[data_name]) # outputs the state of the dataframe with prices and indicators
    number_of_trials = st.sidebar.number_input("Number of Trials", min_value=0, value=50, step=10)
    if Strategy is None:
        st.sidebar.write("Select a Strategy")
        return None
    
    # Make location to hold run data and equities
    data_key = "run_name_" + Strategy.name + st.session_state["name"]
    equity_key = "equities_" + Strategy.name + st.session_state["name"]
    if data_key not in st.session_state:
        st.session_state[data_key] = []
    if equity_key not in st.session_state:
        st.session_state[equity_key] = {}

    

    if st.sidebar.button("Run Trials"):
        progress_text = st.empty()
        st.session_state[data_name] = add_all_indicators(Strategy.param_config, params_range, st.session_state[data_name])
        for i in range(number_of_trials):
            # Get random parameters
            current_choice = random_choice(Strategy, params_range)
            # Test random parameters
            run_strategy(StrategyClass=Strategy, 
                         params=current_choice, 
                         backtest_method=simple_backtest, 
                         data=st.session_state[data_name], 
                         data_location=st.session_state[data_key], 
                         equities_location=st.session_state[equity_key]
                         )
                        
            percentage = round(((i + 1) / number_of_trials) * 100, 2)
            progress_text.write(f"Backtesting Progress: {percentage}%")
    hold_results(st.session_state[data_key])
        

def random_choice(StrategyClass, params):
    '''
    Returns: 
        current_choice (dict) random parameters to be tested within the given range 
    '''
    param_config = StrategyClass.param_config
    current_choice = {}
    
    for parameter, cfg in StrategyClass.param_config.items():
        # Cost per trade is fixed
        if parameter == "cost_per_trade":
            continue
        
        # Handle the indicator case
        elif cfg['type'] == "indicator":
            low, high = params[parameter]
            type_no = random.randint(0, len(cfg['allowed']) - 1)
            indicator_type = cfg['allowed'][type_no]
            window_size = random.randint(low, high)
            current_choice[parameter] = (indicator_type, window_size)
        # Handle all other float cases,
        else:
            low, high = params[parameter]
            choice = round(random.uniform(low, high), 2)
            current_choice[parameter] = choice

    
    return current_choice


def choose_strategy():
    '''
    Choose strategy to optimise, 
    Returns:
        StrategyClass name of strategy 
        Params (dict) min and max for each parameter
    '''

    st.sidebar.header("Choose Strategy to Optimise:")
    strategy_type = st.sidebar.selectbox("Strategy", ["None"] + list(strategy_classes.keys()))

    StrategyClass = None
    params_range: dict = {}

    valid = True   # Track if any parameter has min > max
    errors = []    # Collect error messages

    if strategy_type == "None":
        return StrategyClass, params_range

    StrategyClass = strategy_classes[strategy_type]
    # Put parameter selection into an expandable
    with st.sidebar.expander("Parameter Ranges"):

        for key, cfg in StrategyClass.param_config.items():
            if cfg["label"] == "Cost Per Trade %":
                continue
            elif cfg["type"] == "indicator":
                min_val = st.number_input("min " + cfg["label"], value=5, min_value=0, step=10)
                max_val = st.number_input("max " + cfg["label"], value=50, min_value=0, step=10)

            else: #Just else?
                min_val = round(st.number_input("min " + cfg["label"], value=0.00, min_value=0.00, step=cfg["step"], format="%.2f"), 2)
                max_val = round(st.number_input("max " + cfg["label"], value=0.10, min_value=0.00, step=cfg["step"], format="%.2f"), 2)

            # --- Validation rule ---
            if min_val > max_val:
                valid = False
                errors.append(f"Error: min value is greater than max value")

            params_range[key] = (min_val, max_val)

            # Show accumulated errors
        if not valid:
            with st.container():
                for err in errors:
                    st.error(err)
            st.stop()

    return StrategyClass, params_range



