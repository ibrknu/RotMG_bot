#!/bin/bash

# ROTMG Asset Extractor Setup Script
# This script installs dependencies and prepares the asset extractor

set -e  # Exit on any error

echo "=== ROTMG Asset Extractor Setup ==="
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip3."
    exit 1
fi

echo "pip3 found: $(pip3 --version)"
echo

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements_asset_extractor.txt

# Install exalt-extractor dependencies
echo "Installing exalt-extractor dependencies..."
pip install -r exalt-extractor/requirements.txt

echo
echo "=== Setup Complete ==="
echo
echo "To extract assets, run:"
echo "  source venv/bin/activate"
echo "  python3 asset_extractor.py"
echo
echo "Or with custom game path:"
echo "  python3 asset_extractor.py --game-path /path/to/RotMG\ Exalt_Data"
echo
echo "The extracted assets will be organized in the 'assets/' folder for use with OpenCV." 