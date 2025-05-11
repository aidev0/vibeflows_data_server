#!/bin/bash
set -e

# Clean up Python cache and compiled files
find . -name '__pycache__' -type d -exec rm -rf {} +
find . -name '*.pyc' -delete

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
else
  echo "requirements.txt not found!"
  exit 1
fi

echo "[build.sh] Environment setup complete. To run the server, use ./run.sh" 