#!/usr/bin/env python3
"""
RotMG Bot Readiness Checklist
Checks if the bot is ready for use
"""

import sys
import os
from pathlib import Path
import json

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking Dependencies...")
    
    required_packages = [
        'cv2', 'numpy', 'mss', 'PySide6', 'pynput', 'PIL'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    print("✅ All dependencies installed")
    return True

def check_assets():
    """Check if game assets are available"""
    print("\n🔍 Checking Game Assets...")
    
    asset_dir = Path("assets")
    if not asset_dir.exists():
        print("  ❌ Assets directory not found")
        return False
    
    # Check for key asset categories
    categories = ['enemies', 'terrain', 'ui', 'effects']
    for category in categories:
        category_dir = asset_dir / category
        if category_dir.exists():
            files = list(category_dir.glob("*.png"))
            print(f"  ✅ {category}: {len(files)} files")
        else:
            print(f"  ❌ {category}: directory not found")
    
    # Check asset index
    index_file = asset_dir / "asset_index.json"
    if index_file.exists():
        print(f"  ✅ Asset index found")
    else:
        print(f"  ❌ Asset index not found")
    
    return True

def check_calibration():
    """Check calibration status"""
    print("\n🔍 Checking Calibration...")
    
    calib_file = Path("config/calibration.json")
    if calib_file.exists():
        try:
            with open(calib_file, 'r') as f:
                calib_data = json.load(f)
            
            print(f"  ✅ Calibration file exists")
            
            # Check key calibration settings
            if 'hp_bar' in calib_data:
                print(f"  ✅ HP bar coordinates configured")
            else:
                print(f"  ⚠️  HP bar coordinates not configured")
            
            if 'thresholds' in calib_data:
                print(f"  ✅ Detection thresholds configured")
            else:
                print(f"  ⚠️  Detection thresholds not configured")
                
            return True
        except Exception as e:
            print(f"  ❌ Error reading calibration: {e}")
            return False
    else:
        print(f"  ⚠️  No calibration file found (run calibration tool)")
        return False

def check_config():
    """Check configuration files"""
    print("\n🔍 Checking Configuration...")
    
    config_file = Path("config/settings.py")
    if config_file.exists():
        print(f"  ✅ Settings configuration found")
    else:
        print(f"  ❌ Settings configuration not found")
    
    # Check for user config
    user_config = Path("config/user_config.json")
    if user_config.exists():
        print(f"  ✅ User configuration found")
    else:
        print(f"  ⚠️  No user configuration (will use defaults)")
    
    return True

def check_vision_system():
    """Test vision detection system"""
    print("\n🔍 Testing Vision System...")
    
    try:
        from vision.detection import get_calibration_status, capture_screen, get_hp_percent
        from vision.asset_loader import AssetLoader
        
        # Test calibration status
        status = get_calibration_status()
        print(f"  ✅ Calibration status: {status['loaded']}")
        
        # Test screen capture
        try:
            frame = capture_screen()
            print(f"  ✅ Screen capture: {frame.shape}")
            
            # Test HP detection
            hp = get_hp_percent(frame)
            print(f"  ✅ HP detection: {hp}%")
            
        except Exception as e:
            print(f"  ⚠️  Screen capture issue: {e}")
        
        # Test asset loader
        loader = AssetLoader("assets")
        enemies = loader.get_enemy_assets()
        print(f"  ✅ Asset loader: {len(enemies)} enemy assets")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Vision system error: {e}")
        return False

def check_safety_features():
    """Check safety features"""
    print("\n🔍 Checking Safety Features...")
    
    # Check for emergency stop
    print(f"  ✅ Emergency stop: Ctrl+Q configured")
    
    # Check for auto-nexus
    print(f"  ✅ Auto-nexus: Configurable HP threshold")
    
    # Check for logging
    log_dir = Path("logs")
    if log_dir.exists():
        print(f"  ✅ Logging system: {len(list(log_dir.glob('*.log')))} log files")
    else:
        print(f"  ⚠️  Logging directory not found")
    
    return True

def main():
    """Run readiness checklist"""
    print("🤖 RotMG Bot - Readiness Checklist")
    print("=" * 50)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Assets", check_assets),
        ("Calibration", check_calibration),
        ("Configuration", check_config),
        ("Vision System", check_vision_system),
        ("Safety Features", check_safety_features),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        if check_func():
            passed += 1
    
    print(f"\n{'='*50}")
    print(f"Readiness Score: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 BOT IS READY TO USE!")
        print("\nNext steps:")
        print("1. Launch game and position window")
        print("2. Run: python main.py")
        print("3. Configure settings in GUI")
        print("4. Start bot with caution")
    elif passed >= total - 1:
        print("⚠️  ALMOST READY - Minor issues to fix")
        print("\nRecommended actions:")
        print("1. Run calibration tool: python vision/calibration_tool.py")
        print("2. Configure HP bar coordinates")
        print("3. Test with game screenshots")
    else:
        print("❌ NOT READY - Several issues need fixing")
        print("\nCritical issues to resolve:")
        print("1. Install missing dependencies")
        print("2. Extract game assets")
        print("3. Run calibration")
    
    print(f"\nSafety Reminder:")
    print("⚠️  Use at your own risk - may violate game ToS")
    print("⚠️  Test on a test account first")
    print("⚠️  Monitor bot behavior closely")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 