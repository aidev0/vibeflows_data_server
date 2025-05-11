#!/bin/bash
set -e

# Activate virtual environment
source venv/bin/activate

# Run the application
python -m data_server.app 