#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if not already installed
python3 -m pip install -r test_requirements.txt

# Run the test dashboard
python3 -m uvicorn test_dashboard:app --reload --host 0.0.0.0 --port 8000