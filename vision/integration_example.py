#!/usr/bin/env python3
"""
Integration Example: Using Extracted Assets with ROTMG Bot
This example shows how to integrate the extracted assets with your existing bot
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Import your existing modules
try:
    from vision.detection import DetectionSystem  # Your existing detection system
    from vision.asset_loader import AssetLoader
except ImportError:
    print("Warning: Some modules not found. This is an example file.")
    DetectionSystem = None

logger = logging.getLogger(__name__)


class EnhancedDetectionSystem:
    """Enhanced detection system using extracted assets"""
    
    def __init__(self, assets_path: str = "assets"):
        self.asset_loader = AssetLoader(assets_path)
        self.detection_pipeline = None
        self.matchers = None
        
        # Initialize detection pipeline
        self._initialize_detection_pipeline()
        
    def _initialize_detection_pipeline(self):
        """Initialize the detection pipeline with extracted assets"""
        try:
            self.detection_pipeline, self.matchers = self.asset_loader.create_detection_pipeline()
            logger.info("Detection pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize detection pipeline: {e}")
    
    def detect_enemies(self, screen_image: np.ndarray) -> List[Dict[str, any]]:
        """Detect enemies in the screen image"""
        if not self.matchers or 'enemies' not in self.matchers:
            return []
        
        try:
            enemy_matches = self.matchers['enemies'](screen_image)
            results = []
            
            for enemy_name, matches in enemy_matches.items():
                for x, y, w, h in matches:
                    results.append({
                        'type': 'enemy',
                        'name': enemy_name,
                        'position': (x, y),
                        'size': (w, h),
                        'confidence': 0.8  # You can calculate actual confidence
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error detecting enemies: {e}")
            return []
    
    def detect_projectiles(self, screen_image: np.ndarray) -> List[Dict[str, any]]:
        """Detect projectiles in the screen image"""
        if not self.matchers or 'projectiles' not in self.matchers:
            return []
        
        try:
            projectile_matches = self.matchers['projectiles'](screen_image)
            results = []
            
            for projectile_name, matches in projectile_matches.items():
                for x, y, w, h in matches:
                    results.append({
                        'type': 'projectile',
                        'name': projectile_name,
                        'position': (x, y),
                        'size': (w, h),
                        'confidence': 0.8
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error detecting projectiles: {e}")
            return []
    
    def detect_dangerous_terrain(self, screen_image: np.ndarray) -> List[Dict[str, any]]:
        """Detect dangerous terrain that should be avoided"""
        if not self.matchers or 'dangerous_terrain' not in self.matchers:
            return []
        
        try:
            danger_matches = self.matchers['dangerous_terrain'](screen_image)
            results = []
            
            for danger_name, matches in danger_matches.items():
                for x, y, w, h in matches:
                    results.append({
                        'type': 'dangerous_terrain',
                        'name': danger_name,
                        'position': (x, y),
                        'size': (w, h),
                        'confidence': 0.8
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error detecting dangerous terrain: {e}")
            return []
    
    def detect_safe_terrain(self, screen_image: np.ndarray) -> List[Dict[str, any]]:
        """Detect safe terrain for navigation"""
        if not self.matchers or 'safe_terrain' not in self.matchers:
            return []
        
        try:
            safe_matches = self.matchers['safe_terrain'](screen_image)
            results = []
            
            for safe_name, matches in safe_matches.items():
                for x, y, w, h in matches:
                    results.append({
                        'type': 'safe_terrain',
                        'name': safe_name,
                        'position': (x, y),
                        'size': (w, h),
                        'confidence': 0.8
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error detecting safe terrain: {e}")
            return []
    
    def get_navigation_path(self, screen_image: np.ndarray, target_position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Calculate safe navigation path avoiding dangerous terrain"""
        dangerous_areas = self.detect_dangerous_terrain(screen_image)
        safe_areas = self.detect_safe_terrain(screen_image)
        
        # Simple pathfinding: find safe areas and avoid dangerous ones
        # This is a basic implementation - you might want to use A* or similar
        current_pos = (screen_image.shape[1] // 2, screen_image.shape[0] // 2)  # Assume player is center
        
        # Create a simple path avoiding dangerous areas
        path = [current_pos]
        
        # Add intermediate safe points
        for safe_area in safe_areas:
            safe_pos = safe_area['position']
            # Check if this safe area is between current and target
            if self._is_between_points(current_pos, safe_pos, target_position):
                path.append(safe_pos)
        
        path.append(target_position)
        return path
    
    def _is_between_points(self, start: Tuple[int, int], middle: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """Check if middle point is between start and end points"""
        # Simple distance-based check
        start_to_middle = np.sqrt((middle[0] - start[0])**2 + (middle[1] - start[1])**2)
        middle_to_end = np.sqrt((end[0] - middle[0])**2 + (end[1] - middle[1])**2)
        start_to_end = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        
        # Allow some tolerance for pathfinding
        return start_to_middle + middle_to_end <= start_to_end * 1.5
    
    def analyze_screen(self, screen_image: np.ndarray) -> Dict[str, any]:
        """Comprehensive screen analysis using extracted assets"""
        analysis = {
            'enemies': self.detect_enemies(screen_image),
            'projectiles': self.detect_projectiles(screen_image),
            'dangerous_terrain': self.detect_dangerous_terrain(screen_image),
            'safe_terrain': self.detect_safe_terrain(screen_image),
            'recommendations': []
        }
        
        # Generate recommendations based on detected objects
        if analysis['enemies']:
            analysis['recommendations'].append({
                'type': 'combat',
                'message': f"Found {len(analysis['enemies'])} enemies nearby",
                'priority': 'high'
            })
        
        if analysis['projectiles']:
            analysis['recommendations'].append({
                'type': 'evasion',
                'message': f"Detected {len(analysis['projectiles'])} projectiles - dodge!",
                'priority': 'critical'
            })
        
        if analysis['dangerous_terrain']:
            analysis['recommendations'].append({
                'type': 'navigation',
                'message': f"Avoid {len(analysis['dangerous_terrain'])} dangerous areas",
                'priority': 'high'
            })
        
        return analysis


# Example usage with your existing bot
def integrate_with_bot():
    """Example of how to integrate with your existing bot"""
    
    # Initialize enhanced detection system
    enhanced_detection = EnhancedDetectionSystem()
    
    # Example: Screen capture (you would use your existing screen capture method)
    def capture_screen():
        """Capture screen - replace with your existing method"""
        # This is a placeholder - use your existing screen capture
        return np.zeros((800, 600, 3), dtype=np.uint8)  # Placeholder
    
    # Example: Main bot loop
    def bot_loop():
        """Main bot loop using enhanced detection"""
        while True:
            # Capture screen
            screen = capture_screen()
            
            # Analyze screen with extracted assets
            analysis = enhanced_detection.analyze_screen(screen)
            
            # Handle recommendations
            for recommendation in analysis['recommendations']:
                if recommendation['priority'] == 'critical':
                    # Handle critical situations (dodge projectiles, etc.)
                    print(f"CRITICAL: {recommendation['message']}")
                elif recommendation['priority'] == 'high':
                    # Handle high priority situations
                    print(f"HIGH: {recommendation['message']}")
            
            # Example: Navigate to a target while avoiding danger
            target_position = (400, 300)  # Example target
            safe_path = enhanced_detection.get_navigation_path(screen, target_position)
            
            # Use the path for navigation
            if safe_path:
                print(f"Safe path to target: {safe_path}")
            
            # Continue with your existing bot logic...
            break  # Remove this in actual implementation


# Example: Testing the system
def test_enhanced_detection():
    """Test the enhanced detection system"""
    print("Testing Enhanced Detection System...")
    
    # Initialize system
    enhanced_detection = EnhancedDetectionSystem()
    
    # Create a test image
    test_image = np.zeros((600, 800, 3), dtype=np.uint8)
    
    # Test detection methods
    enemies = enhanced_detection.detect_enemies(test_image)
    projectiles = enhanced_detection.detect_projectiles(test_image)
    dangerous_terrain = enhanced_detection.detect_dangerous_terrain(test_image)
    
    print(f"Detected {len(enemies)} enemies")
    print(f"Detected {len(projectiles)} projectiles")
    print(f"Detected {len(dangerous_terrain)} dangerous terrain areas")
    
    # Test screen analysis
    analysis = enhanced_detection.analyze_screen(test_image)
    print(f"Analysis complete with {len(analysis['recommendations'])} recommendations")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Test the system
    test_enhanced_detection()
    
    print("\nIntegration example completed!")
    print("To use with your bot:")
    print("1. Extract assets using: python3 asset_extractor.py")
    print("2. Import EnhancedDetectionSystem in your bot")
    print("3. Use the detection methods in your main bot loop") 