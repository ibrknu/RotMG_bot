#!/usr/bin/env python3
"""
Simple test version of the Linux RotMG Bot
This version has minimal functionality to test basic operation
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

def test_simple_bot():
    """Test a simplified version of the bot"""
    print("🧪 Testing Simple Linux RotMG Bot...")
    
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
        
        # Test simple bot loop (just a few iterations)
        print("🔄 Testing simple bot loop...")
        bot._running = True
        loop_count = 0
        max_loops = 10
        
        while bot._running and loop_count < max_loops:
            try:
                loop_count += 1
                print(f"  Loop {loop_count}/{max_loops}")
                
                # Simple screen capture
                frame = bot.capture_game_screen()
                if frame is not None:
                    print(f"    ✅ Captured frame: {frame.shape}")
                else:
                    print(f"    ❌ Frame capture failed")
                
                # Simple HP detection
                try:
                    from vision import detection
                    hp = detection.get_hp_percent(frame) if frame is not None else None
                    print(f"    📊 HP: {hp}%")
                except Exception as e:
                    print(f"    ⚠️  HP detection failed: {e}")
                
                time.sleep(0.5)  # Wait between loops
                
            except Exception as e:
                print(f"    ❌ Loop error: {e}")
                break
        
        # Stop the bot
        bot.stop()
        print("✅ Simple bot test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing bot: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_simple_bot()
    sys.exit(0 if success else 1) 