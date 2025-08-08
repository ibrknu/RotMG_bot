#!/usr/bin/env python3
"""
Test suite for vision detection components
"""

import unittest
import cv2
import numpy as np
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from vision.detection import (
    capture_screen, find_enemies, find_bullets, find_loot, 
    get_hp_percent, infer_player_class, find_obstacles,
    inventory_is_full, find_worst_item_slot, get_item_value,
    is_bullet_dangerous, get_dodge_direction
)
from vision.asset_loader import AssetLoader

class TestVisionDetection(unittest.TestCase):
    """Test cases for vision detection functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
        # Initialize asset loader
        cls.asset_loader = AssetLoader("assets")
        
        # Create test images directory
        cls.test_images_dir = Path("tests/test_images")
        cls.test_images_dir.mkdir(exist_ok=True)
        
        # Create a test image if none exists
        cls.create_test_image()
        
    @classmethod
    def create_test_image(cls):
        """Create a test image for testing if none exists"""
        test_image_path = cls.test_images_dir / "test_screen.png"
        
        if not test_image_path.exists():
            # Create a synthetic test image (1920x1080)
            test_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
            
            # Add a red HP bar at the bottom left
            cv2.rectangle(test_image, (50, 900), (250, 920), (0, 0, 255), -1)
            
            # Add some colored rectangles to simulate enemies
            cv2.rectangle(test_image, (500, 300), (550, 350), (0, 0, 255), -1)  # Red enemy
            cv2.rectangle(test_image, (800, 400), (850, 450), (0, 0, 255), -1)  # Another red enemy
            
            # Add blue circles to simulate bullets
            cv2.circle(test_image, (600, 500), 5, (255, 0, 0), -1)
            cv2.circle(test_image, (700, 600), 5, (255, 0, 0), -1)
            
            # Add yellow rectangles to simulate loot
            cv2.rectangle(test_image, (300, 600), (350, 650), (0, 255, 255), -1)
            
            cv2.imwrite(str(test_image_path), test_image)
            logging.info(f"Created test image: {test_image_path}")
    
    def setUp(self):
        """Set up for each test"""
        self.test_image_path = self.test_images_dir / "test_screen.png"
        self.test_image = cv2.imread(str(self.test_image_path))
        self.assertIsNotNone(self.test_image, "Test image should be loaded")
        
    def test_capture_screen(self):
        """Test screen capture functionality"""
        try:
            frame = capture_screen()
            self.assertIsNotNone(frame, "Screen capture should return a frame")
            self.assertEqual(len(frame.shape), 3, "Frame should be 3D (height, width, channels)")
            self.assertEqual(frame.shape[2], 3, "Frame should have 3 color channels (BGR)")
        except Exception as e:
            self.skipTest(f"Screen capture not available: {e}")
    
    def test_hp_detection(self):
        """Test HP bar detection"""
        hp_percent = get_hp_percent(self.test_image)
        
        # HP detection should return a value between 0 and 100, or None
        if hp_percent is not None:
            self.assertIsInstance(hp_percent, (int, float), "HP should be numeric")
            self.assertGreaterEqual(hp_percent, 0, "HP should be >= 0")
            self.assertLessEqual(hp_percent, 100, "HP should be <= 100")
        
        logging.info(f"HP Detection test result: {hp_percent}%")
    
    def test_enemy_detection(self):
        """Test enemy detection"""
        enemies = find_enemies(self.test_image)
        
        self.assertIsInstance(enemies, list, "Enemies should be a list")
        
        for enemy in enemies:
            self.assertIn('center', enemy, "Enemy should have center coordinates")
            self.assertIn('distance', enemy, "Enemy should have distance")
            self.assertIn('name', enemy, "Enemy should have a name")
            
            center = enemy['center']
            self.assertIsInstance(center, tuple, "Center should be a tuple")
            self.assertEqual(len(center), 2, "Center should have 2 coordinates")
            
            self.assertIsInstance(enemy['distance'], (int, float), "Distance should be numeric")
            self.assertGreaterEqual(enemy['distance'], 0, "Distance should be >= 0")
        
        logging.info(f"Enemy detection test result: {len(enemies)} enemies found")
    
    def test_bullet_detection(self):
        """Test bullet/projectile detection"""
        bullets = find_bullets(self.test_image)
        
        self.assertIsInstance(bullets, list, "Bullets should be a list")
        
        for bullet in bullets:
            self.assertIn('center', bullet, "Bullet should have center coordinates")
            self.assertIn('name', bullet, "Bullet should have a name")
            
            center = bullet['center']
            self.assertIsInstance(center, tuple, "Center should be a tuple")
            self.assertEqual(len(center), 2, "Center should have 2 coordinates")
        
        logging.info(f"Bullet detection test result: {len(bullets)} bullets found")
    
    def test_loot_detection(self):
        """Test loot detection"""
        loot_items = find_loot(self.test_image)
        
        self.assertIsInstance(loot_items, list, "Loot items should be a list")
        
        for item in loot_items:
            self.assertIn('center', item, "Loot item should have center coordinates")
            self.assertIn('name', item, "Loot item should have a name")
            
            center = item['center']
            self.assertIsInstance(center, tuple, "Center should be a tuple")
            self.assertEqual(len(center), 2, "Center should have 2 coordinates")
        
        logging.info(f"Loot detection test result: {len(loot_items)} items found")
    
    def test_obstacle_detection(self):
        """Test obstacle detection"""
        obstacles = find_obstacles(self.test_image)
        
        self.assertIsInstance(obstacles, list, "Obstacles should be a list")
        
        for obstacle in obstacles:
            self.assertIn('center', obstacle, "Obstacle should have center coordinates")
            self.assertIn('name', obstacle, "Obstacle should have a name")
        
        logging.info(f"Obstacle detection test result: {len(obstacles)} obstacles found")
    
    def test_player_class_inference(self):
        """Test player class inference"""
        player_class = infer_player_class(self.test_image)
        
        # Should return a string or None
        if player_class is not None:
            self.assertIsInstance(player_class, str, "Player class should be a string")
            self.assertGreater(len(player_class), 0, "Player class should not be empty")
        
        logging.info(f"Player class inference test result: {player_class}")
    
    def test_inventory_full_detection(self):
        """Test inventory full detection"""
        is_full = inventory_is_full(self.test_image)
        
        self.assertIsInstance(is_full, bool, "Inventory full should be boolean")
        
        logging.info(f"Inventory full detection test result: {is_full}")
    
    def test_worst_item_slot_detection(self):
        """Test worst item slot detection"""
        worst_slot = find_worst_item_slot(self.test_image)
        
        # Should return an integer slot number or None
        if worst_slot is not None:
            self.assertIsInstance(worst_slot, int, "Worst slot should be an integer")
            self.assertGreaterEqual(worst_slot, 0, "Slot number should be >= 0")
        
        logging.info(f"Worst item slot detection test result: {worst_slot}")
    
    def test_item_value_lookup(self):
        """Test item value lookup"""
        # Test with known items
        test_items = ["Potion of Life", "Wooden Sword", "Unknown Item"]
        
        for item_name in test_items:
            value = get_item_value(item_name)
            
            # Should return an integer value or -1 for unknown items
            self.assertIsInstance(value, int, "Item value should be an integer")
            
            if value != -1:  # Known item
                self.assertGreaterEqual(value, 0, "Item value should be >= 0")
        
        logging.info(f"Item value lookup test completed for {len(test_items)} items")
    
    def test_bullet_danger_assessment(self):
        """Test bullet danger assessment"""
        # Create test bullets
        test_bullets = [
            {'center': (960, 540)},  # At player center (dangerous)
            {'center': (100, 100)},  # Far from player (safe)
            {'center': (950, 530)},  # Close to player (dangerous)
        ]
        
        for bullet in test_bullets:
            is_dangerous = is_bullet_dangerous(bullet)
            self.assertIsInstance(is_dangerous, bool, "Danger assessment should be boolean")
            
            logging.info(f"Bullet at {bullet['center']} - Dangerous: {is_dangerous}")
    
    def test_dodge_direction_calculation(self):
        """Test dodge direction calculation"""
        # Create test bullets at different positions
        test_bullets = [
            {'center': (960, 440)},  # Above player
            {'center': (960, 640)},  # Below player
            {'center': (860, 540)},  # Left of player
            {'center': (1060, 540)}, # Right of player
        ]
        
        valid_directions = ['up', 'down', 'left', 'right']
        
        for bullet in test_bullets:
            direction = get_dodge_direction(bullet)
            
            self.assertIsInstance(direction, str, "Dodge direction should be a string")
            self.assertIn(direction, valid_directions, f"Dodge direction should be one of {valid_directions}")
            
            logging.info(f"Bullet at {bullet['center']} - Dodge direction: {direction}")
    
    def test_asset_loader_functionality(self):
        """Test asset loader functionality"""
        # Test getting assets by category
        enemy_assets = self.asset_loader.get_enemy_assets()
        self.assertIsInstance(enemy_assets, list, "Enemy assets should be a list")
        
        projectile_assets = self.asset_loader.get_projectile_assets()
        self.assertIsInstance(projectile_assets, list, "Projectile assets should be a list")
        
        terrain_assets = self.asset_loader.get_terrain_assets()
        self.assertIsInstance(terrain_assets, list, "Terrain assets should be a list")
        
        logging.info(f"Asset loader test - Enemies: {len(enemy_assets)}, Projectiles: {len(projectile_assets)}, Terrain: {len(terrain_assets)}")
    
    def test_detection_pipeline_creation(self):
        """Test detection pipeline creation"""
        pipeline, matchers = self.asset_loader.create_detection_pipeline()
        
        self.assertIsInstance(pipeline, dict, "Pipeline should be a dictionary")
        self.assertIsInstance(matchers, dict, "Matchers should be a dictionary")
        
        # Check that pipeline has expected categories
        expected_categories = ['enemies', 'projectiles', 'dangerous_terrain', 'safe_terrain', 'ui_elements']
        for category in expected_categories:
            self.assertIn(category, pipeline, f"Pipeline should contain {category}")
        
        logging.info(f"Detection pipeline created with {len(pipeline)} categories and {len(matchers)} matchers")


class TestVisionPerformance(unittest.TestCase):
    """Performance tests for vision detection"""
    
    def setUp(self):
        """Set up for performance tests"""
        self.test_image = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        self.asset_loader = AssetLoader("assets")
    
    def test_detection_speed(self):
        """Test detection speed for real-time performance"""
        import time
        
        # Test HP detection speed
        start_time = time.time()
        for _ in range(10):
            get_hp_percent(self.test_image)
        hp_time = time.time() - start_time
        
        # Test enemy detection speed
        start_time = time.time()
        for _ in range(10):
            find_enemies(self.test_image)
        enemy_time = time.time() - start_time
        
        # Test bullet detection speed
        start_time = time.time()
        for _ in range(10):
            find_bullets(self.test_image)
        bullet_time = time.time() - start_time
        
        # All detections should complete within reasonable time (e.g., < 100ms per frame)
        max_time_per_frame = 0.1  # 100ms
        
        self.assertLess(hp_time / 10, max_time_per_frame, f"HP detection too slow: {hp_time/10:.3f}s per frame")
        self.assertLess(enemy_time / 10, max_time_per_frame, f"Enemy detection too slow: {enemy_time/10:.3f}s per frame")
        self.assertLess(bullet_time / 10, max_time_per_frame, f"Bullet detection too slow: {bullet_time/10:.3f}s per frame")
        
        logging.info(f"Performance test - HP: {hp_time/10:.3f}s, Enemies: {enemy_time/10:.3f}s, Bullets: {bullet_time/10:.3f}s per frame")


def run_vision_tests():
    """Run all vision detection tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestVisionDetection))
    test_suite.addTest(unittest.makeSuite(TestVisionPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Vision Detection Test Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_vision_tests()
    sys.exit(0 if success else 1) 