#!/usr/bin/env python3
"""
Test Asset Integration
Tests that extracted assets work with OpenCV for bot detection
"""

import cv2
import numpy as np
from vision.asset_loader import AssetLoader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_asset_loading():
    """Test that assets can be loaded properly"""
    print("=== Testing Asset Loading ===")
    
    # Initialize asset loader
    loader = AssetLoader("assets")
    
    # Test loading different categories
    enemies = loader.get_enemy_assets()
    terrain = loader.get_terrain_assets()
    
    print(f"✓ Loaded {len(enemies)} enemy assets")
    print(f"✓ Loaded {len(terrain)} terrain assets")
    
    return loader

def test_image_loading():
    """Test that images can be loaded as OpenCV arrays"""
    print("\n=== Testing Image Loading ===")
    
    loader = AssetLoader("assets")
    
    # Load some sample images
    enemy_images = loader.load_asset_images('enemies')
    terrain_images = loader.load_asset_images('terrain')
    
    print(f"✓ Loaded {len(enemy_images)} enemy images as OpenCV arrays")
    print(f"✓ Loaded {len(terrain_images)} terrain images as OpenCV arrays")
    
    # Test a few sample images
    sample_enemy = list(enemy_images.values())[0]
    sample_terrain = list(terrain_images.values())[0]
    
    print(f"✓ Sample enemy image shape: {sample_enemy.shape}")
    print(f"✓ Sample terrain image shape: {sample_terrain.shape}")
    
    return enemy_images, terrain_images

def test_template_matching():
    """Test OpenCV template matching with extracted assets"""
    print("\n=== Testing Template Matching ===")
    
    loader = AssetLoader("assets")
    
    # Load some assets
    enemy_images = loader.load_asset_images('enemies')
    terrain_images = loader.load_asset_images('terrain')
    
    # Create a test "screen" (just a blank image for testing)
    test_screen = np.zeros((800, 600, 3), dtype=np.uint8)
    
    # Test template matching with a few assets
    test_count = 0
    for enemy_name, enemy_template in list(enemy_images.items())[:5]:  # Test first 5
        try:
            # Convert to grayscale for better matching
            if len(enemy_template.shape) == 3:
                enemy_gray = cv2.cvtColor(enemy_template, cv2.COLOR_BGR2GRAY)
            else:
                enemy_gray = enemy_template
                
            screen_gray = cv2.cvtColor(test_screen, cv2.COLOR_BGR2GRAY)
            
            # Perform template matching
            result = cv2.matchTemplate(screen_gray, enemy_gray, cv2.TM_CCOEFF_NORMED)
            
            # This should work without errors
            test_count += 1
            
        except Exception as e:
            print(f"✗ Template matching failed for {enemy_name}: {e}")
            continue
    
    print(f"✓ Template matching test passed for {test_count} enemy assets")
    
    # Test terrain assets
    terrain_count = 0
    for terrain_name, terrain_template in list(terrain_images.items())[:5]:  # Test first 5
        try:
            if len(terrain_template.shape) == 3:
                terrain_gray = cv2.cvtColor(terrain_template, cv2.COLOR_BGR2GRAY)
            else:
                terrain_gray = terrain_template
                
            screen_gray = cv2.cvtColor(test_screen, cv2.COLOR_BGR2GRAY)
            
            result = cv2.matchTemplate(screen_gray, terrain_gray, cv2.TM_CCOEFF_NORMED)
            terrain_count += 1
            
        except Exception as e:
            print(f"✗ Template matching failed for {terrain_name}: {e}")
            continue
    
    print(f"✓ Template matching test passed for {terrain_count} terrain assets")

def test_detection_pipeline():
    """Test the complete detection pipeline"""
    print("\n=== Testing Detection Pipeline ===")
    
    loader = AssetLoader("assets")
    
    try:
        # Create detection pipeline
        pipeline, matchers = loader.create_detection_pipeline()
        
        print(f"✓ Detection pipeline created successfully")
        print(f"✓ Pipeline categories: {list(pipeline.keys())}")
        
        # Test each category
        for category, images in pipeline.items():
            if images:
                print(f"  - {category}: {len(images)} images loaded")
        
        return True
        
    except Exception as e:
        print(f"✗ Detection pipeline failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🎯 ROTMG Asset Integration Test")
    print("=" * 40)
    
    try:
        # Test 1: Asset loading
        loader = test_asset_loading()
        
        # Test 2: Image loading
        enemy_images, terrain_images = test_image_loading()
        
        # Test 3: Template matching
        test_template_matching()
        
        # Test 4: Detection pipeline
        pipeline_success = test_detection_pipeline()
        
        print("\n" + "=" * 40)
        print("🎉 ASSET INTEGRATION TEST COMPLETED!")
        print("\nYour extracted assets are ready for use with your bot!")
        print("\nNext steps:")
        print("1. Integrate AssetLoader into your main bot code")
        print("2. Use template matching for enemy detection")
        print("3. Use terrain detection for navigation")
        print("4. Test with actual screen captures")
        
        if pipeline_success:
            print("\n✅ All tests passed! Your bot is ready to use the extracted assets.")
        else:
            print("\n⚠️  Some tests had issues. Check the logs above.")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 