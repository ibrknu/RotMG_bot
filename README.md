# RotMG Bot

A computer vision-based bot for Realm of the Mad God (RotMG) that provides automated gameplay assistance.

## Features

- **Auto-Nexus**: Automatically nexus when HP drops below threshold
- **Enemy Detection**: Computer vision-based enemy and projectile detection
- **Movement Assistance**: Kiting and circle-strafing movement patterns
- **GUI Interface**: User-friendly control panel
- **Configurable**: Customizable keybindings and settings
- **Emergency Stop**: Quick shutdown functionality

## Prerequisites

- Windows 10/11
- Python 3.8+ (with virtual environment)
- RotMG game client
- Administrative privileges (for input simulation)

## Quick Setup

### 1. Install Dependencies
```bash
# Run the setup script
python setup_bot.py
```

### 2. Test Installation
```bash
# Verify everything works
python test_bot_startup.py
```

### 3. Calibrate HP Bar (Recommended)
```bash
# Launch the HP calibration tool
python calibrate_hp.py
```

### 4. Start the Bot
```bash
# Launch the bot GUI
python main.py
```

## Configuration

### HP Bar Region
The bot needs to know where your HP bar is located on screen. Edit `config/user_config.json`:

```json
{
  "hp_bar_region": {
    "x": 50,      // X coordinate of HP bar
    "y": 900,     // Y coordinate of HP bar  
    "width": 200, // Width of HP bar
    "height": 20  // Height of HP bar
  }
}
```

### Keybindings
Configure your game controls in `config/user_config.json`:

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

## Usage

1. **Start RotMG** and log into your character
2. **Launch the bot**: `python main.py`
3. **Configure settings** in the GUI:
   - Set auto-nexus HP threshold
   - Choose movement mode (Kiting/Circle-Strafe)
   - Select your character class
4. **Click "Start Bot"** to begin
5. **Use Emergency Stop** if needed: `python emergency_stop.py`

## Safety Features

- **Emergency Stop**: Press F12 or run `emergency_stop.py`
- **User Input Priority**: Bot stops when you press keys
- **Configurable Thresholds**: Safe auto-nexus levels
- **Logging**: All actions logged to `logs/bot.log`

## Troubleshooting

### Common Issues

1. **"Python not found"**
   - Activate virtual environment: `.venv\Scripts\activate`
   - Or use: `.venv\bin\python main.py`

2. **"Import errors"**
   - Run: `python setup_bot.py`
   - Check: `python test_bot_startup.py`

3. **"HP detection not working"**
   - Calibrate HP bar region in config
   - Use debug mode to find correct coordinates

4. **"Window not detected"**
   - Ensure RotMG is running
   - Check window title matches config
   - Try fullscreen mode

### Debug Mode

Enable debug logging by editing `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## File Structure

```
RotMG_bot/
├── main.py              # Main entry point
├── run_bot.bat          # Easy launcher
├── setup_bot.py         # Setup script
├── test_bot_startup.py  # Startup test
├── calibrate_hp.py      # HP bar calibration tool
├── calibrate_hp.bat     # HP calibration launcher
├── emergency_stop.py    # Emergency stop
├── config/
│   └── settings.py      # Configuration management
├── gui/
│   └── window.py        # GUI interface
├── logic/
│   └── bot.py           # Core bot logic
├── vision/
│   ├── detection.py     # Computer vision
│   └── asset_loader.py  # Asset management
├── input/
│   ├── keyboard.py      # Keyboard input
│   └── mouse.py         # Mouse input
└── assets/              # Game assets
```

## Disclaimer

This bot is for educational purposes. Use at your own risk. The developers are not responsible for any account bans or other consequences.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is provided as-is for educational purposes. 