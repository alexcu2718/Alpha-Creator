#!/usr/bin/env bash
set -e  # Exit immediately if a command fails

VENV_DIR=".venv"



# Ensure uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi


if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    uv venv "$VENV_DIR" --python=3.13 #avoid reinstall if not existing
else
    echo "Virtual environment already exists."
fi



if [[ "$OS" == "Windows_NT" ]]; then
    source "$VENV_DIR/Scripts/activate"
else
    source "$VENV_DIR/bin/activate"
fi
uv sync --frozen #sync the dependencies


uv run  streamlit run main.py
