# 💹 AlphaCreator – Streamlit Crypto Backtester

**AlphaCreator** is an interactive **Streamlit web app** for building, testing, and visualizing cryptocurrency trading strategies.

It combines a clean interface with modular Python architecture:
- Fetch crypto price data using `yfinance`
- Add indicators (SMA, EMA, RSI)
- Run strategy backtests with customizable parameters
- Visualize equity curves and performance stats
- Save, compare, and manage backtest results

---

## 🧠 Features

- 📈 **Multiple Strategies** – Mean Reversion, Momentum, RSI, Bollinger  
- ⚙️ **Modular Design** – Easily add new strategies or indicators  
- 💾 **Save & Compare Runs** – Track multiple backtests visually  
- 🧮 **Performance Metrics** – Profit %, Sharpe ratio, Win rate, Drawdown  
- 🖥️ **Clean UI** – Streamlit front-end with automatic caching  

---

## 🗂️ Project Structure

```text
AlphaCreator/
│
├── main.py                # Streamlit entry point
│
├── core/                  # Backtesting & analytics logic
│   ├── backtester.py
│   ├── data_loader.py
│   ├── graphsandstats.py
│   ├── indicators.py
│   └── strategy_holder.py
│
├── ui/                    # Streamlit user interface
│   ├── sidebar.py
│   └── plots.py
│
├── utils/                 # Session & result helpers
│   ├── session.py
│   └── results.py
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### Clone the repository
```bash
git clone https://github.com/SimonGFleet/Alpha-Creator.git
cd Alpha-Creator
```

### (Optional) Create and activate a virtual environment
**Create the environment:**
```bash
python -m venv .venv
```

**On macOS/Linux:**
```bash
source .venv/bin/activate
```

**On Windows:**
```bash
.venv\Scripts\activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the app
```bash
streamlit run main.py
```
