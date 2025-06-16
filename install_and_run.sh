#!/bin/bash

# Exit if any command fails
set -e

# Go to script directory
cd "$(dirname "$0")"

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run the app
echo "Running image_converter.py..."
python image_converter.py

