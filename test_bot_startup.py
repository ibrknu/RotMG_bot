#!/usr/bin/env python3
"""
Simple test script to verify bot startup
"""
import sys
import os
import traceback

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from PySide6.QtWidgets import QApplication
        print("✅ PySide6 imported successfully")
    except ImportError as e:
        print(f"❌ PySide6 import failed: {e}")
        return False
    
    try:
        from gui.window import BotWindow
        print("✅ GUI window imported successfully")
    except ImportError as e:
        print(f"❌ GUI window import failed: {e}")
        return False
    
    try:
        from config import settings
        print("✅ Config settings imported successfully")
    except ImportError as e:
        print(f"❌ Config settings import failed: {e}")
        return False
    
    try:
        from logic.bot import RotMGbot
        print("✅ Bot logic imported successfully")
    except ImportError as e:
        print(f"❌ Bot logic import failed: {e}")
        return False
    
    try:
        from vision.detection import get_hp_percent, find_enemies
        print("✅ Vision detection imported successfully")
    except ImportError as e:
        print(f"❌ Vision detection import failed: {e}")
        return False
    
    try:
        from input import keyboard, mouse
        print("✅ Input modules imported successfully")
    except ImportError as e:
        print(f"❌ Input modules import failed: {e}")
        return False
    
    return True

def test_config_loading():
    """Test if configuration can be loaded"""
    print("\nTesting configuration loading...")
    
    try:
        from config import settings
        config = settings.load_config()
        print("✅ Configuration loaded successfully")
        print(f"   Auto-nexus threshold: {config.get('auto_nexus_percent', 'N/A')}%")
        print(f"   Movement mode: {config.get('movement_mode', 'N/A')}")
        print(f"   Player class: {config.get('player_class', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_asset_loading():
    """Test if assets can be loaded"""
    print("\nTesting asset loading...")
    
    try:
        from vision.asset_loader import AssetLoader
        loader = AssetLoader("assets")
        print("✅ Asset loader created successfully")
        
        # Test if asset index exists
        if loader.asset_index:
            print(f"   Found {len(loader.asset_index.get('enemies', []))} enemy assets")
            print(f"   Found {len(loader.asset_index.get('projectiles', []))} projectile assets")
        else:
            print("   ⚠️  No asset index found")
        
        return True
    except Exception as e:
        print(f"❌ Asset loading failed: {e}")
        return False

def test_gui_creation():
    """Test if GUI can be created (without showing it)"""
    print("\nTesting GUI creation...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from gui.window import BotWindow
        from config import settings
        
        # Create a minimal Qt application
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Load config
        config = settings.load_config()
        
        # Create window (but don't show it)
        window = BotWindow(config)
        print("✅ GUI window created successfully")
        
        # Clean up
        window.deleteLater()
        
        return True
    except Exception as e:
        print(f"❌ GUI creation failed: {e}")
        print(traceback.format_exc())
        return False

def main():
    """Run all tests"""
    print("=== RotMG Bot Startup Test ===\n")
    
    tests = [
        test_imports,
        test_config_loading,
        test_asset_loading,
        test_gui_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"=== Test Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("✅ All tests passed! The bot should be ready to run.")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Configure HP bar region if needed")
        print("3. Start RotMG and test the bot")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Run: python setup_bot.py")
        print("2. Install missing dependencies")
        print("3. Check file permissions")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 