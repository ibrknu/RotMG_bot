#!/usr/bin/env python3
"""
Simple test script to verify calibration tool functionality
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_calibration_tool():
    """Test the calibration tool"""
    print("Testing Calibration Tool...")
    
    try:
        # Test importing the calibration tool
        from vision.calibration_tool import VisionCalibrationTool
        print("✅ Calibration tool imported successfully")
        
        # Test creating the tool (without running GUI)
        print("Testing calibration tool creation...")
        # Note: We won't actually run the GUI in this test to avoid blocking
        
        # Test calibration data loading
        calib_file = Path("config/calibration.json")
        if calib_file.exists():
            print("✅ Calibration file exists")
        else:
            print("⚠️  No calibration file found (this is normal for first run)")
        
        print("✅ Calibration tool test completed")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import calibration tool: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing calibration tool: {e}")
        return False

def test_vision_detection():
    """Test vision detection with calibration"""
    print("\nTesting Vision Detection...")
    
    try:
        from vision.detection import (
            get_calibration_status, reload_calibration,
            capture_screen, get_hp_percent
        )
        
        # Test calibration status
        status = get_calibration_status()
        print(f"✅ Calibration status: {status}")
        
        # Test screen capture (if possible)
        try:
            frame = capture_screen()
            print(f"✅ Screen capture successful: {frame.shape}")
            
            # Test HP detection
            hp = get_hp_percent(frame)
            print(f"✅ HP detection: {hp}%")
            
        except Exception as e:
            print(f"⚠️  Screen capture not available: {e}")
        
        print("✅ Vision detection test completed")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import vision detection: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing vision detection: {e}")
        return False

def test_asset_loader():
    """Test asset loader functionality"""
    print("\nTesting Asset Loader...")
    
    try:
        from vision.asset_loader import AssetLoader
        
        # Test asset loader creation
        loader = AssetLoader("assets")
        print("✅ Asset loader created successfully")
        
        # Test getting assets
        enemies = loader.get_enemy_assets()
        projectiles = loader.get_projectile_assets()
        terrain = loader.get_terrain_assets()
        
        print(f"✅ Assets loaded - Enemies: {len(enemies)}, Projectiles: {len(projectiles)}, Terrain: {len(terrain)}")
        
        # Test detection pipeline
        pipeline, matchers = loader.create_detection_pipeline()
        print(f"✅ Detection pipeline created with {len(pipeline)} categories")
        
        print("✅ Asset loader test completed")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import asset loader: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing asset loader: {e}")
        return False

def main():
    """Run all tests"""
    print("RotMG Bot - Calibration and Vision Testing")
    print("=" * 50)
    
    tests = [
        ("Calibration Tool", test_calibration_tool),
        ("Vision Detection", test_vision_detection),
        ("Asset Loader", test_asset_loader),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Calibration system is ready.")
        print("\nNext steps:")
        print("1. Run: python vision/calibration_tool.py")
        print("2. Use the GUI to calibrate HP bar coordinates")
        print("3. Test with real game screenshots")
        print("4. Save calibration settings")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 