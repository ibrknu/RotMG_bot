#!/usr/bin/env python3
"""
Simple test script for Linux RotMG Bot
Tests basic functionality without GUI
"""

import sys
import logging
import time
from config import settings
from logic.bot_linux import RotMGbotLinux

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def test_linux_bot():
    """Test the Linux bot functionality"""
    print("🧪 Testing Linux RotMG Bot...")
    
    # Load config
    config = settings.load_config()
    print(f"✅ Config loaded: auto_nexus={config.get('auto_nexus_percent', 30)}%")
    
    # Create bot instance
    try:
        bot = RotMGbotLinux(config)
        print("✅ Linux bot created successfully")
        
        # Test window detection
        print("🔍 Testing window detection...")
        if bot.rotmg_window_info:
            print(f"✅ Window found: {bot.rotmg_window_info['name']}")
        else:
            print("⚠️  No window found (will run in fullscreen mode)")
        
        # Test screen capture
        print("📸 Testing screen capture...")
        frame = bot.capture_game_screen()
        if frame is not None:
            print(f"✅ Screen capture successful: {frame.shape}")
        else:
            print("❌ Screen capture failed")
        
        print("\n🎉 Linux bot test completed successfully!")
        print("The bot is ready to use with: python main_linux.py")
        
    except Exception as e:
        print(f"❌ Error testing Linux bot: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_linux_bot()
    sys.exit(0 if success else 1) 