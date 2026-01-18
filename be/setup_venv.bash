#!/bin/bash

# Exit on error
set +e

echo "Setting up Python virtual environment..."

# 1. Check if venv already exists
if [ -d "venv" ]; then
    echo "Virtual environment 'venv' already exists. Skipping creation."
else
    echo "Creating new virtual environment..."
    python3.11 -m venv venv
    echo "Virtual environment created successfully."
fi

# 2. Activate the environment
echo "Activating virtual environment..."
source venv/bin/activate

# 3. Upgrade pip (Critical for finding wheels)
echo "Upgrading pip..."
pip install --upgrade pip

# 4. Check if PROJ is installed (required for pyproj)
if ! command -v proj &> /dev/null; then
    echo "WARNING: PROJ is not installed. This is required for pyproj."
    echo "Installing PROJ via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install proj
        echo "PROJ installed successfully."
    else
        echo "ERROR: Homebrew is not installed. Please install PROJ manually:"
        echo "  brew install proj"
        echo "Or visit: https://pyproj4.github.io/pyproj/stable/installation.html"
        exit 1
    fi
else
    echo "PROJ is already installed."
fi

# 5. Install requirements
echo "Installing requirements from requirements.txt..."
pip install -r requirements.txt

echo "Setup complete! Virtual environment is ready."
echo "To activate the environment manually, run: source venv/bin/activate"