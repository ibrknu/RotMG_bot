#!/usr/bin/env python3
"""
Simple test to verify the bot can start and run
"""
import time
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(__file__))

def test_bot_direct():
    """Test the bot directly without GUI"""
    try:
        from logic.bot import RotMGbot
        from config import settings
        
        print("Loading config...")
        config = settings.load_config()
        print(f"Config: {config}")
        
        print("Creating bot instance...")
        bot = RotMGbot(config)
        print("Bot created successfully!")
        
        print("Starting bot for 5 seconds...")
        # Start bot in a separate thread
        import threading
        bot_thread = threading.Thread(target=bot.run)
        bot_thread.daemon = True
        bot_thread.start()
        
        # Let it run for 5 seconds
        time.sleep(5)
        
        print("Stopping bot...")
        bot.stop()
        
        print("Bot test completed!")
        return True
        
    except Exception as e:
        print(f"Bot test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Simple Bot Test ===")
    success = test_bot_direct()
    if success:
        print("✅ Bot test passed!")
    else:
        print("❌ Bot test failed!") 