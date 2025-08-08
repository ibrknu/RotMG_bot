# Quick Start Guide - RotMG Bot

## ✅ Setup Complete!

The bot has been successfully set up and is ready to use.

## 🚀 How to Run

### Option 1: Double-click the launcher
- Double-click `run_bot.bat` to start the bot

### Option 2: Command line
```bash
venv\Scripts\python.exe main.py
```

## ⚙️ Configuration

### 1. HP Bar Calibration (IMPORTANT)
The bot needs to know where your HP bar is located. Edit `config/user_config.json`:

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

**To find your HP bar coordinates:**
1. Take a screenshot of RotMG
2. Use any image editor to find the coordinates of your HP bar
3. Update the config file with those coordinates

### 2. Keybindings
Make sure your game controls match the config:

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

## 🎮 Usage

1. **Start RotMG** and log into your character
2. **Launch the bot** using one of the methods above
3. **Configure settings** in the GUI:
   - Set auto-nexus threshold (recommended: 30%)
   - Choose movement mode (Kiting/Circle-Strafe)
   - Select your character class
4. **Click "Start Bot"** to begin
5. **Use Emergency Stop** if needed: `python emergency_stop.py`

## 🛡️ Safety Features

- **Emergency Stop**: Press F12 or run `emergency_stop.py`
- **User Input Priority**: Bot stops when you press keys
- **Configurable Thresholds**: Safe auto-nexus levels
- **Logging**: All actions logged to `logs/bot.log`

## 🔧 Troubleshooting

### Bot won't start
- Run: `venv\Scripts\python.exe test_bot_startup.py`
- Check: `logs/bot.log` for errors

### HP detection not working
- Calibrate HP bar region in config
- Try different coordinates

### Window not detected
- Ensure RotMG is running
- Try fullscreen mode
- Check window title matches config

## 📁 Files

- `main.py` - Main bot file
- `run_bot.bat` - Easy launcher
- `config/user_config.json` - Configuration
- `logs/bot.log` - Log file
- `emergency_stop.py` - Emergency stop

## ⚠️ Disclaimer

This bot is for educational purposes. Use at your own risk. 