#!/bin/bash

# 1. Create venv if it doesn't exist
[ ! -d ".env" ] && python3 -m venv .env

# 2. Activate the environment
source .env/bin/activate

# 3. Upgrade pip (Critical for finding wheels)
pip install --upgrade pip

# 4. Install requirements
pip install -r requirements.txt