#!/usr/bin/env python3
"""
Test to show that the bot can send keyboard and mouse input
"""
import time
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(__file__))

def test_bot_actions():
    """Test bot actions"""
    try:
        from logic.bot import RotMGbot
        from config import settings
        
        print("Testing bot actions...")
        print("This will test keyboard and mouse input")
        print("Make sure you have a text editor or game window focused!")
        
        config = settings.load_config()
        bot = RotMGbot(config)
        
        print("Bot created. Testing actions in 3 seconds...")
        time.sleep(3)
        
        # Test keyboard input
        print("Testing keyboard input (WASD)...")
        for key in ['w', 'a', 's', 'd']:
            print(f"Pressing {key}...")
            bot.keyboard.tap_key(key)
            time.sleep(0.5)
        
        # Test mouse movement
        print("Testing mouse movement...")
        current_pos = bot.mouse.position
        print(f"Current mouse position: {current_pos}")
        
        # Move mouse to center
        center_x, center_y = 960, 540
        bot.mouse.position = (center_x, center_y)
        print(f"Moved mouse to center: ({center_x}, {center_y})")
        
        time.sleep(1)
        
        # Test mouse click
        print("Testing mouse click...")
        bot.mouse.click(button='left')
        print("Left click completed!")
        
        print("Action test completed!")
        return True
        
    except Exception as e:
        print(f"Action test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Bot Action Test ===")
    print("This will test keyboard and mouse input")
    success = test_bot_actions()
    if success:
        print("✅ Action test passed!")
    else:
        print("❌ Action test failed!") 