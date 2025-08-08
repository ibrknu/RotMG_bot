# RotMG Bot - Linux/Proton Edition

A Linux-optimized bot for Realm of the Mad God running through Proton compatibility layer.

## 🐧 Linux-Specific Features

- **Proton Compatibility**: Optimized for RotMG running through Steam Proton
- **Linux Window Management**: Uses `xdotool` for window detection and focus
- **No Windows Dependencies**: Removed all Windows-specific modules (`win32gui`, etc.)
- **Screenshot Calibration**: Easy calibration using game screenshots
- **Auto Window Detection**: Automatically finds RotMG window regardless of Proton window title

## 🚀 Quick Start

### 1. Install System Dependencies
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv xdotool
```

### 2. Setup Bot
```bash
chmod +x setup_linux.sh
./setup_linux.sh
```

### 3. Launch RotMG
- Start Steam
- Launch RotMG through Proton
- Make sure the game window is visible

### 4. Run Bot
```bash
source venv/bin/activate
python main_linux.py
```

## 🎯 Features

### ✅ **Core Functionality**
- **Screen Analysis**: Captures and analyzes game screen
- **HP Monitoring**: Tracks health percentage with auto-nexus
- **Enemy Detection**: Recognizes 966 different enemy types
- **Bullet Dodging**: Automatic projectile avoidance
- **Loot Collection**: Smart item pickup and inventory management
- **Movement Control**: WASD movement with kiting/circle-strafe strategies

### ✅ **Linux Optimizations**
- **Window Detection**: Automatically finds RotMG window through Proton
- **Focus Management**: Keeps game window focused during operation
- **Screen Capture**: Optimized for Linux display servers (X11/Wayland)
- **Input Handling**: Linux-compatible keyboard and mouse control

### ✅ **Safety Features**
- **Emergency Stop**: Press `Ctrl+Q` to stop immediately
- **Auto-Nexus**: Configurable HP threshold (default: 30%)
- **Comprehensive Logging**: All activities logged to `logs/bot_linux.log`
- **Error Recovery**: Graceful handling of window focus issues

## ⚙️ Configuration

### HP Bar Calibration
The bot automatically detects HP bar coordinates from your user config:
```json
{
  "hp_bar_region": {
    "x": 50,
    "y": 900,
    "width": 200,
    "height": 20
  }
}
```

### Key Bindings
```json
{
  "keybinds": {
    "move_up": "w",
    "move_down": "s", 
    "move_left": "a",
    "move_right": "d",
    "attack": "left",
    "nexus": "r"
  }
}
```

## 🛠️ Troubleshooting

### Window Not Found
If the bot can't find the RotMG window:
1. Make sure RotMG is running through Proton
2. Check window title: `xdotool search --name "RotMG"`
3. Try running in fullscreen mode

### Permission Issues
```bash
# If xdotool fails, check permissions
xhost +local:root
```

### Screen Capture Issues
```bash
# For Wayland users, ensure X11 compatibility
export QT_QPA_PLATFORM=xcb
```

## 📁 Project Structure

```
RotMG_bot/
├── main_linux.py              # Linux-specific main entry point
├── logic/bot_linux.py         # Linux-optimized bot logic
├── vision/                    # Computer vision components
├── input/                     # Input automation
├── gui/                       # PySide6 GUI
├── config/                    # Configuration files
├── assets/                    # Game assets (enemies, terrain)
├── logs/                      # Log files
├── tests/                     # Test suite
├── requirements_linux.txt     # Linux dependencies
├── setup_linux.sh            # Linux setup script
└── screenshot_calibration.py # Screenshot-based calibration tool
```

## 🔧 Advanced Usage

### Screenshot Calibration
For precise HP bar calibration:
```bash
python screenshot_calibration.py
```

### Custom Window Detection
Add custom window titles in `config/user_config.json`:
```json
{
  "window_detection": {
    "window_titles": [
      "RotMG",
      "Realm of the Mad God",
      "Your Custom Window Title"
    ]
  }
}
```

### Performance Tuning
- Adjust detection thresholds in calibration
- Modify loop timing for different performance levels
- Configure asset loading for memory optimization

## ⚠️ Important Notes

### Legal Disclaimer
- This bot is for educational purposes only
- Use at your own risk
- May violate RotMG's Terms of Service
- Test on a test account first

### System Requirements
- **OS**: Linux (Ubuntu 20.04+, Debian 11+, etc.)
- **Python**: 3.8+
- **Steam**: With Proton compatibility layer
- **Display**: X11 or Wayland with X11 compatibility

### Proton Compatibility
- Tested with Proton 7.0+
- Works with both Steam and standalone Proton
- Supports various Proton versions and configurations

## 🐛 Known Issues

1. **Wayland**: Some features may require X11 compatibility mode
2. **Multiple Monitors**: Window detection optimized for primary monitor
3. **High DPI**: May require scaling adjustments for 4K displays

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test on Linux with Proton
4. Submit a pull request

## 📄 License

This project is for educational purposes. Please respect RotMG's terms of service.

---

**Happy Botting on Linux! 🐧🎮** 