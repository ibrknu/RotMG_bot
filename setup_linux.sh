#!/bin/bash

echo "Setting up RotMG Bot for Linux/Proton..."

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "Error: This script is for Linux systems only"
    exit 1
fi

# Install system dependencies
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3-pip python3-venv xdotool

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements_linux.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p config
mkdir -p tests/test_images

# Set up logging
echo "Setting up logging..."
touch logs/bot_linux.log

# Make scripts executable
chmod +x main_linux.py
chmod +x screenshot_calibration.py

echo "Setup complete!"
echo ""
echo "To run the bot:"
echo "  source venv/bin/activate"
echo "  python main_linux.py"
echo ""
echo "To calibrate with screenshots:"
echo "  python screenshot_calibration.py"
echo ""
echo "Note: Make sure RotMG is running through Proton before starting the bot" 