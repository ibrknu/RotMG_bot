#!/usr/bin/env python3
"""
Test to verify class selection functionality
"""
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(__file__))

def test_class_selection():
    """Test class selection functionality"""
    try:
        from logic.bot import RotMGbot
        from config import settings
        
        print("Testing class selection...")
        
        # Test with different classes
        test_classes = ["Wizard", "Warrior", "Archer", "Knight"]
        
        for test_class in test_classes:
            print(f"\nTesting with class: {test_class}")
            
            # Create config with specific class
            config = settings.load_config()
            config['player_class'] = test_class
            
            # Create bot instance
            bot = RotMGbot(config)
            
            # Verify class was set correctly
            if bot.player_class == test_class:
                print(f"✅ Class set correctly: {bot.player_class}")
            else:
                print(f"❌ Class mismatch: expected {test_class}, got {bot.player_class}")
                return False
        
        print("\n✅ All class selection tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Class selection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Class Selection Test ===")
    success = test_class_selection()
    if success:
        print("✅ Class selection test completed successfully!")
    else:
        print("❌ Class selection test failed!") 