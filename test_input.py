#!/usr/bin/env python3
"""
Simple test script to verify keyboard and mouse input works
"""
import time
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(__file__))

from input import keyboard, mouse

def test_keyboard_input():
    """Test basic keyboard input"""
    print("Testing keyboard input...")
    print("You should see 'w' pressed in 3 seconds...")
    time.sleep(3)
    
    # Test pressing 'w' key
    keyboard.tap_key('w')
    print("Pressed 'w' key")
    
    time.sleep(1)
    print("Testing WASD movement...")
    
    # Test movement keys
    for key in ['w', 'a', 's', 'd']:
        print(f"Pressing {key}...")
        keyboard.tap_key(key)
        time.sleep(0.5)
    
    print("Keyboard test completed!")

def test_mouse_input():
    """Test basic mouse input"""
    print("\nTesting mouse input...")
    print("Mouse will move to center of screen in 3 seconds...")
    time.sleep(3)
    
    # Get current mouse position
    current_pos = mouse.Controller().position
    print(f"Current mouse position: {current_pos}")
    
    # Move to center of screen (assuming 1920x1080)
    center_x, center_y = 960, 540
    mouse.move_to(center_x, center_y)
    print(f"Moved mouse to center: ({center_x}, {center_y})")
    
    time.sleep(1)
    
    # Test clicking
    print("Testing left click...")
    mouse.click(button='left')
    print("Left click completed!")
    
    print("Mouse test completed!")

def test_bot_initialization():
    """Test if the bot can be initialized without errors"""
    print("\nTesting bot initialization...")
    try:
        from logic.bot import RotMGbot
        from config import settings
        
        config = settings.load_config()
        print(f"Config loaded: {config}")
        
        bot = RotMGbot(config)
        print("Bot initialized successfully!")
        
        return True
    except Exception as e:
        print(f"Bot initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("=== ROTMG Bot Input Test ===")
    
    # Test bot initialization first
    if not test_bot_initialization():
        print("Bot initialization failed, stopping tests.")
        sys.exit(1)
    
    # Test keyboard input
    test_keyboard_input()
    
    # Test mouse input
    test_mouse_input()
    
    print("\n=== All tests completed! ===")
    print("If you saw keyboard/mouse activity, input is working correctly.") 