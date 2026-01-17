#!/bin/bash

# 1. Create venv if it doesn't exist
[ ! -d "venv" ] && python3 -m venv venv

# 2. Activate the environment
source venv/bin/activate

# 3. Upgrade pip (Critical for finding wheels)
pip install --upgrade pip
    
# 4. Install requirements
pip install -r requirements.txt