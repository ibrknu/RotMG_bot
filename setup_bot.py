#!/usr/bin/env python3
"""
Setup script for RotMG Bot
Installs dependencies and configures the environment
"""
import subprocess
import sys
import os
import json

def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    
    # Core dependencies needed for the bot
    core_deps = [
        "PySide6==6.9.1",
        "opencv-python==4.12.0.88",
        "numpy>=2.2.0",
        "mss==10.0.0",
        "pynput==1.7.6",
        "pywin32>=307",
        "pytesseract==0.3.10",
        "Pillow==10.4.0",
        "psutil==5.9.8"
    ]
    
    for dep in core_deps:
        try:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {dep}: {e}")
            return False
    
    print("✅ Dependencies installed successfully!")
    return True

def create_default_config():
    """Create a default configuration file if it doesn't exist"""
    config_path = "config/user_config.json"
    
    if os.path.exists(config_path):
        print("✅ Configuration file already exists")
        return True
    
    default_config = {
        "auto_nexus_percent": 30,
        "movement_mode": "Kiting",
        "player_class": "Wizard",
        "keybinds": {
            "move_up": "w",
            "move_down": "s",
            "move_left": "a",
            "move_right": "d",
            "attack": "left",
            "nexus": "r",
            "drop_item": None
        },
        "hp_bar_region": {
            "x": 50,
            "y": 900,
            "width": 200,
            "height": 20
        },
        "window_detection": {
            "window_titles": [
                "RotMG", "Realm of the Mad God", "Realm", 
                "RotMG - Realm of the Mad God", "RotMG Exalt",
                "Realm of the Mad God Exalt"
            ]
        }
    }
    
    try:
        os.makedirs("config", exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        print("✅ Default configuration created")
        return True
    except Exception as e:
        print(f"❌ Failed to create config: {e}")
        return False

def verify_assets():
    """Verify that required assets are available"""
    print("Verifying assets...")
    
    required_files = [
        "assets/asset_index.json",
        "assets/metadata/spritesheet.json"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing required asset: {file_path}")
            return False
    
    print("✅ Assets verified")
    return True

def main():
    """Main setup function"""
    print("=== RotMG Bot Setup ===\n")
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return False
    
    # Create default config
    if not create_default_config():
        print("❌ Failed to create configuration")
        return False
    
    # Verify assets
    if not verify_assets():
        print("❌ Asset verification failed")
        return False
    
    print("\n✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run: python main.py")
    print("2. Configure HP bar region in config/user_config.json")
    print("3. Adjust keybindings if needed")
    print("4. Start RotMG and test the bot")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 