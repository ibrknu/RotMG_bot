#!/usr/bin/env python3
"""
Asset Loader for ROTMG Bot
Loads and manages extracted game assets for OpenCV-based detection
"""

import os
import json
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class AssetLoader:
    """Loads and manages game assets for bot use"""
    
    def __init__(self, assets_path: str = "assets"):
        self.assets_path = Path(assets_path)
        self.asset_index = {}
        self.loaded_assets = {}
        self.spritesheet_data = {}
        
        # Load asset index
        self._load_asset_index()
        
        # Load spritesheet data
        self._load_spritesheet_data()
        
    def _load_asset_index(self):
        """Load the asset index file"""
        index_file = self.assets_path / "asset_index.json"
        
        if not index_file.exists():
            logger.warning(f"Asset index not found at {index_file}")
            return
            
        try:
            with open(index_file, 'r') as f:
                self.asset_index = json.load(f)
            logger.info("Asset index loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load asset index: {e}")
    
    def _load_spritesheet_data(self):
        """Load spritesheet metadata"""
        spritesheet_file = self.assets_path / "metadata" / "spritesheet.json"
        
        if not spritesheet_file.exists():
            logger.warning(f"Spritesheet data not found at {spritesheet_file}")
            return
            
        try:
            with open(spritesheet_file, 'r') as f:
                self.spritesheet_data = json.load(f)
            logger.info("Spritesheet data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load spritesheet data: {e}")
    
    def get_assets_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all assets in a specific category"""
        return self.asset_index.get(category, [])
    
    def load_image_asset(self, asset_path: str) -> Optional[np.ndarray]:
        """Load an image asset as OpenCV format"""
        full_path = self.assets_path / asset_path
        
        if not full_path.exists():
            logger.warning(f"Asset not found: {full_path}")
            return None
            
        try:
            # Load image with OpenCV
            image = cv2.imread(str(full_path))
            if image is None:
                logger.error(f"Failed to load image: {full_path}")
                return None
                
            return image
        except Exception as e:
            logger.error(f"Error loading image {full_path}: {e}")
            return None
    
    def get_enemy_assets(self) -> List[Dict[str, Any]]:
        """Get all enemy-related assets"""
        return self.get_assets_by_category('enemies')
    
    def get_projectile_assets(self) -> List[Dict[str, Any]]:
        """Get all projectile-related assets"""
        return self.get_assets_by_category('projectiles')
    
    def get_terrain_assets(self) -> List[Dict[str, Any]]:
        """Get all terrain-related assets"""
        return self.get_assets_by_category('terrain')
    
    def get_ui_assets(self) -> List[Dict[str, Any]]:
        """Get all UI-related assets"""
        return self.get_assets_by_category('ui')
    
    def get_effect_assets(self) -> List[Dict[str, Any]]:
        """Get all effect-related assets"""
        return self.get_assets_by_category('effects')
    
    def find_asset_by_name(self, name: str, category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find an asset by name, optionally within a specific category"""
        if category:
            assets = self.get_assets_by_category(category)
        else:
            # Search all categories
            assets = []
            for cat_assets in self.asset_index.values():
                assets.extend(cat_assets)
        
        for asset in assets:
            if asset['name'].lower() == name.lower():
                return asset
        
        return None
    
    def load_asset_images(self, category: str) -> Dict[str, np.ndarray]:
        """Load all image assets from a category"""
        assets = self.get_assets_by_category(category)
        loaded_images = {}
        
        for asset in assets:
            if asset['type'] in ['png', 'jpg', 'jpeg']:
                image = self.load_image_asset(asset['path'])
                if image is not None:
                    loaded_images[asset['name']] = image
        
        logger.info(f"Loaded {len(loaded_images)} images from category '{category}'")
        return loaded_images
    
    def get_sprite_info(self, sprite_name: str) -> Optional[Dict[str, Any]]:
        """Get sprite information from spritesheet data"""
        return self.spritesheet_data.get(sprite_name)
    
    def create_template_matcher(self, template_image: np.ndarray, threshold: float = 0.8):
        """Create a template matching function for a specific image"""
        def match_template(screen_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
            """
            Match template in screen image
            Returns list of (x, y, width, height) matches
            """
            # Check if template is smaller than screen image
            if template_image.shape[0] > screen_image.shape[0] or template_image.shape[1] > screen_image.shape[1]:
                logger.warning(f"Template size {template_image.shape} is larger than screen size {screen_image.shape}, skipping")
                return []
            
            # Convert images to grayscale for better matching
            if len(template_image.shape) == 3:
                template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
            else:
                template_gray = template_image
                
            if len(screen_image.shape) == 3:
                screen_gray = cv2.cvtColor(screen_image, cv2.COLOR_BGR2GRAY)
            else:
                screen_gray = screen_image
            
            try:
                # Perform template matching
                result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
                
                # Find locations where matching exceeds threshold
                locations = np.where(result >= threshold)
                matches = []
                
                for pt in zip(*locations[::-1]):  # Switch columns and rows
                    x, y = pt
                    w, h = template_gray.shape[::-1]
                    matches.append((x, y, w, h))
                
                return matches
            except cv2.error as e:
                logger.error(f"OpenCV error in template matching: {e}")
                return []
        
        return match_template
    
    def create_multi_template_matcher(self, asset_names: List[str], category: str = "enemies", threshold: float = 0.8):
        """Create a matcher that can detect multiple asset types"""
        templates = {}
        
        for name in asset_names:
            asset = self.find_asset_by_name(name, category)
            if asset and asset['type'] in ['png', 'jpg', 'jpeg']:
                image = self.load_image_asset(asset['path'])
                if image is not None:
                    templates[name] = self.create_template_matcher(image, threshold)
        
        def match_multiple_templates(screen_image: np.ndarray) -> Dict[str, List[Tuple[int, int, int, int]]]:
            """Match multiple templates in screen image"""
            results = {}
            
            for name, matcher in templates.items():
                matches = matcher(screen_image)
                if matches:
                    results[name] = matches
            
            return results
        
        return match_multiple_templates
    
    def get_damage_indicators(self) -> Dict[str, np.ndarray]:
        """Get assets that indicate damage or dangerous terrain"""
        damage_assets = {}
        
        # Load terrain assets that might be dangerous
        terrain_images = self.load_asset_images('terrain')
        for name, image in terrain_images.items():
            if any(keyword in name.lower() for keyword in ['lava', 'spike', 'trap', 'danger', 'damage']):
                damage_assets[name] = image
        
        # Load projectile assets
        projectile_images = self.load_asset_images('projectiles')
        damage_assets.update(projectile_images)
        
        return damage_assets
    
    def get_navigation_assets(self) -> Dict[str, np.ndarray]:
        """Get assets useful for navigation (safe terrain, paths, etc.)"""
        nav_assets = {}
        
        # Load terrain assets that are safe
        terrain_images = self.load_asset_images('terrain')
        for name, image in terrain_images.items():
            if any(keyword in name.lower() for keyword in ['ground', 'floor', 'path', 'safe', 'walkable']):
                nav_assets[name] = image
        
        return nav_assets
    
    def create_detection_pipeline(self):
        """Create a comprehensive detection pipeline for the bot"""
        pipeline = {
            'enemies': self.load_asset_images('enemies'),
            'projectiles': self.load_asset_images('projectiles'),
            'dangerous_terrain': self.get_damage_indicators(),
            'safe_terrain': self.get_navigation_assets(),
            'ui_elements': self.load_asset_images('ui')
        }
        
        # Create matchers for each category
        matchers = {}
        for category, images in pipeline.items():
            if images:
                matchers[category] = self.create_multi_template_matcher(
                    list(images.keys()), 
                    category='enemies' if category == 'enemies' else 'projectiles' if category == 'projectiles' else 'terrain'
                )
        
        return pipeline, matchers


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize asset loader
    loader = AssetLoader()
    
    # Print available assets
    print("Available asset categories:")
    for category, assets in loader.asset_index.items():
        print(f"  {category}: {len(assets)} assets")
    
    # Example: Load enemy assets
    enemies = loader.get_enemy_assets()
    print(f"\nFound {len(enemies)} enemy assets")
    
    # Example: Create detection pipeline
    pipeline, matchers = loader.create_detection_pipeline()
    print(f"\nDetection pipeline created with {len(pipeline)} categories") 