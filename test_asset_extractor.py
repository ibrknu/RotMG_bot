#!/usr/bin/env python3
"""
Test script for ROTMG Asset Extractor
Tests the extractor functionality without requiring actual game files
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def test_asset_extractor_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test basic imports
        import json
        import logging
        from pathlib import Path
        print("✓ Basic imports successful")
        
        # Test OpenCV
        import cv2
        import numpy as np
        print("✓ OpenCV imports successful")
        
        # Test asset loader
        sys.path.append(os.path.dirname(__file__))
        from vision.asset_loader import AssetLoader
        print("✓ Asset loader import successful")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_asset_loader_functionality():
    """Test asset loader functionality with mock data"""
    print("\nTesting asset loader functionality...")
    
    try:
        # Create temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            test_assets_dir = Path(temp_dir) / "test_assets"
            test_assets_dir.mkdir()
            
            # Create test asset index
            test_index = {
                "enemies": [
                    {"name": "test_enemy", "path": "enemies/test_enemy.png", "type": "png"}
                ],
                "terrain": [
                    {"name": "test_terrain", "path": "terrain/test_terrain.png", "type": "png"}
                ]
            }
            
            # Create test directories and files
            (test_assets_dir / "enemies").mkdir()
            (test_assets_dir / "terrain").mkdir()
            (test_assets_dir / "metadata").mkdir()
            
            # Create test asset index file
            with open(test_assets_dir / "asset_index.json", 'w') as f:
                import json
                json.dump(test_index, f)
            
            # Create test spritesheet data
            test_spritesheet = {
                "test_sprite": {
                    "x": 0, "y": 0, "width": 32, "height": 32
                }
            }
            
            with open(test_assets_dir / "metadata" / "spritesheet.json", 'w') as f:
                json.dump(test_spritesheet, f)
            
            # Test asset loader
            from vision.asset_loader import AssetLoader
            loader = AssetLoader(str(test_assets_dir))
            
            # Test basic functionality
            enemies = loader.get_enemy_assets()
            terrain = loader.get_terrain_assets()
            
            assert len(enemies) == 1, f"Expected 1 enemy, got {len(enemies)}"
            assert len(terrain) == 1, f"Expected 1 terrain, got {len(terrain)}"
            
            print("✓ Asset loader functionality test passed")
            return True
            
    except Exception as e:
        print(f"✗ Asset loader test failed: {e}")
        return False

def test_extractor_structure():
    """Test that the extractor has the correct structure"""
    print("\nTesting extractor structure...")
    
    try:
        # Check if main extractor file exists
        if not os.path.exists("asset_extractor.py"):
            print("✗ asset_extractor.py not found")
            return False
        
        # Check if asset loader exists
        if not os.path.exists("vision/asset_loader.py"):
            print("✗ vision/asset_loader.py not found")
            return False
        
        # Check if requirements file exists
        if not os.path.exists("requirements_asset_extractor.txt"):
            print("✗ requirements_asset_extractor.txt not found")
            return False
        
        # Check if setup script exists
        if not os.path.exists("setup_asset_extractor.sh"):
            print("✗ setup_asset_extractor.sh not found")
            return False
        
        print("✓ All required files present")
        return True
        
    except Exception as e:
        print(f"✗ Structure test failed: {e}")
        return False

def test_exalt_extractor_integration():
    """Test integration with exalt-extractor"""
    print("\nTesting exalt-extractor integration...")
    
    try:
        # Check if exalt-extractor directory exists
        if not os.path.exists("exalt-extractor"):
            print("✗ exalt-extractor directory not found")
            return False
        
        # Check if key files exist
        required_files = [
            "exalt-extractor/extractor.py",
            "exalt-extractor/utils/__init__.py",
            "exalt-extractor/utils/Resources.py",
            "exalt-extractor/utils/Extractor.py",
            "exalt-extractor/requirements.txt"
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                print(f"✗ {file_path} not found")
                return False
        
        print("✓ Exalt-extractor integration test passed")
        return True
        
    except Exception as e:
        print(f"✗ Exalt-extractor integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== ROTMG Asset Extractor Test Suite ===\n")
    
    tests = [
        ("Import Test", test_asset_extractor_imports),
        ("Asset Loader Test", test_asset_loader_functionality),
        ("Structure Test", test_extractor_structure),
        ("Exalt-Extractor Integration Test", test_exalt_extractor_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The asset extractor is ready to use.")
        print("\nNext steps:")
        print("1. Run: ./setup_asset_extractor.sh")
        print("2. Activate virtual environment: source venv/bin/activate")
        print("3. Extract assets: python3 asset_extractor.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 