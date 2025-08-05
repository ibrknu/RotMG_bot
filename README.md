# RotMG Bot

A comprehensive bot for Realm of the Mad God (RotMG) that includes asset extraction, vision detection, and automated gameplay capabilities.

## Features

- **Asset Extraction**: Extract and process game assets from RotMG client files
- **Computer Vision**: Detect game elements using OpenCV and image processing
- **Input Automation**: Keyboard and mouse input automation for gameplay
- **GUI Interface**: PySide6-based user interface for bot control
- **Logging System**: Comprehensive logging for debugging and monitoring

## Project Structure

```
RotMG_bot/
├── asset_extractor.py      # Main asset extraction script
├── assets/                 # Extracted game assets
├── config/                 # Configuration files
├── exalt-extractor/        # Unity asset extraction tools
├── gui/                    # GUI components
├── input/                  # Input automation modules
├── logic/                  # Core bot logic
├── logs/                   # Log files
├── main.py                 # Main application entry point
├── output/                 # Output files
├── RotMG-SpriteRenderer/   # Sprite rendering utilities
└── vision/                 # Computer vision modules
```

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd RotMG_bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Asset Extraction
```bash
python asset_extractor.py
```

### Main Bot Application
```bash
python main.py
```

## Dependencies

- Python 3.8+
- OpenCV (cv2)
- PySide6
- NumPy
- PIL (Pillow)
- pynput
- mss
- UnityPy
- And more (see requirements.txt)

## Configuration

Edit `config/settings.py` to customize bot behavior and settings.

## Logging

Logs are stored in the `logs/` directory with timestamps for easy debugging.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for educational purposes. Please respect the terms of service of Realm of the Mad God.

## Disclaimer

This bot is for educational and research purposes only. Use at your own risk and in accordance with the game's terms of service. 