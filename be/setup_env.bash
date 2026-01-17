#!/bin/bash

DIR=".env"

# 1. Create virtual environment if it doesn't exist
if [ ! -d "$DIR" ]; then
  # Checks for python3 first, falls back to python
  if command -v python3 &>/dev/null; then
    python3 -m venv "$DIR"
  else
    python -m venv "$DIR"
  fi
fi

# 2. Activate the environment
# Handles standard Linux/macOS (bin) or Windows GitBash (Scripts)
if [ -f "$DIR/bin/activate" ]; then
    source "$DIR/bin/activate"
elif [ -f "$DIR/Scripts/activate" ]; then
    source "$DIR/Scripts/activate"
else
    echo "Error: Virtual environment activation script not found."
    exit 1
fi

# 3. Install requirements
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "requirements.txt not found, skipping installation."
fi