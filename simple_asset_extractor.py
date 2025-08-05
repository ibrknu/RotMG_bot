#!/usr/bin/env python3
"""
Simple ROTMG Asset Extractor
A more robust extractor that focuses on essential assets for bot use
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional
import argparse

# Add exalt-extractor to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'exalt-extractor'))

try:
    import UnityPy
    from PIL import Image
    import cv2
    import numpy as np
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure all dependencies are installed")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/simple_asset_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SimpleAssetExtractor:
    """Simple and robust asset extractor for ROTMG"""
    
    def __init__(self, game_path: str, output_path: str = "assets"):
        self.game_path = Path(game_path)
        self.output_path = Path(output_path)
        
        # Create output directories
        self._create_output_dirs()
        
    def _create_output_dirs(self):
        """Create organized output directory structure"""
        dirs = [
            "enemies",
            "projectiles", 
            "terrain",
            "ui",
            "effects",
            "metadata",
            "spritesheets"
        ]
        
        for dir_name in dirs:
            (self.output_path / dir_name).mkdir(parents=True, exist_ok=True)
            
        logger.info(f"Created output directory structure in {self.output_path}")
    
    def extract_assets(self):
        """Extract assets using UnityPy directly"""
        logger.info("Starting simple asset extraction...")
        
        try:
            # Find all Unity asset files
            asset_files = []
            for file_path in self.game_path.glob("*"):
                if file_path.is_file() and file_path.suffix in ['.assets', '.resS']:
                    asset_files.append(file_path)
            
            logger.info(f"Found {len(asset_files)} asset files to process")
            
            extracted_count = 0
            
            for asset_file in asset_files:
                try:
                    logger.info(f"Processing {asset_file.name}...")
                    extracted = self._extract_from_file(asset_file)
                    extracted_count += extracted
                except Exception as e:
                    logger.warning(f"Failed to process {asset_file.name}: {e}")
                    continue
            
            logger.info(f"Extracted {extracted_count} assets total")
            
            # Create asset index
            self._create_asset_index()
            
            logger.info("Simple asset extraction completed!")
            
        except Exception as e:
            logger.error(f"Asset extraction failed: {e}")
            raise
    
    def _extract_from_file(self, asset_file: Path) -> int:
        """Extract assets from a single Unity asset file"""
        extracted_count = 0
        
        try:
            # Load the asset file
            env = UnityPy.load(str(asset_file))
            
            for obj in env.objects:
                try:
                    if obj.type.name == "Texture2D":
                        extracted_count += self._extract_texture2d(obj, asset_file.stem)
                    elif obj.type.name == "TextAsset":
                        extracted_count += self._extract_textasset(obj, asset_file.stem)
                    elif obj.type.name == "Sprite":
                        extracted_count += self._extract_sprite(obj, asset_file.stem)
                except Exception as e:
                    logger.debug(f"Failed to extract object {obj.type.name}: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Failed to load {asset_file.name}: {e}")
            
        return extracted_count
    
    def _extract_texture2d(self, obj, source_name: str) -> int:
        """Extract Texture2D assets"""
        try:
            data = obj.read()
            
            # Get texture name
            texture_name = getattr(data, 'name', f"{source_name}_texture_{obj.path_id}")
            
            # Save as PNG
            if hasattr(data, 'image') and data.image:
                output_path = self._get_output_path(texture_name, 'terrain')
                data.image.save(output_path, 'PNG')
                logger.info(f"Extracted texture: {texture_name}")
                return 1
                
        except Exception as e:
            logger.debug(f"Failed to extract Texture2D: {e}")
            
        return 0
    
    def _extract_textasset(self, obj, source_name: str) -> int:
        """Extract TextAsset assets"""
        try:
            data = obj.read()
            
            # Get asset name
            asset_name = getattr(data, 'name', f"{source_name}_text_{obj.path_id}")
            
            # Check if it's JSON or XML
            if hasattr(data, 'script') and data.script:
                content = data.script.decode('utf-8', errors='ignore')
                
                if content.strip().startswith('{') or content.strip().startswith('['):
                    # JSON file
                    output_path = self.output_path / "metadata" / f"{asset_name}.json"
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"Extracted JSON: {asset_name}")
                    return 1
                elif content.strip().startswith('<'):
                    # XML file
                    output_path = self.output_path / "metadata" / f"{asset_name}.xml"
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"Extracted XML: {asset_name}")
                    return 1
                    
        except Exception as e:
            logger.debug(f"Failed to extract TextAsset: {e}")
            
        return 0
    
    def _extract_sprite(self, obj, source_name: str) -> int:
        """Extract Sprite assets"""
        try:
            data = obj.read()
            
            # Get sprite name
            sprite_name = getattr(data, 'name', f"{source_name}_sprite_{obj.path_id}")
            
            # Save as PNG
            if hasattr(data, 'image') and data.image:
                output_path = self._get_output_path(sprite_name, 'enemies')
                data.image.save(output_path, 'PNG')
                logger.info(f"Extracted sprite: {sprite_name}")
                return 1
                
        except Exception as e:
            logger.debug(f"Failed to extract Sprite: {e}")
            
        return 0
    
    def _get_output_path(self, asset_name: str, category: str) -> Path:
        """Get the output path for an asset"""
        # Clean the asset name
        clean_name = "".join(c for c in asset_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_name = clean_name.replace(' ', '_')
        
        return self.output_path / category / f"{clean_name}.png"
    
    def _create_asset_index(self):
        """Create an index of all extracted assets"""
        logger.info("Creating asset index...")
        
        index = {
            'enemies': [],
            'projectiles': [],
            'terrain': [],
            'ui': [],
            'effects': [],
            'metadata': []
        }
        
        # Scan each category directory
        for category in index.keys():
            category_dir = self.output_path / category
            if category_dir.exists():
                for file_path in category_dir.glob("*"):
                    if file_path.is_file():
                        index[category].append({
                            'name': file_path.stem,
                            'path': str(file_path.relative_to(self.output_path)),
                            'type': file_path.suffix[1:],
                            'size': file_path.stat().st_size
                        })
        
        # Save index
        index_file = self.output_path / "asset_index.json"
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
            
        logger.info(f"Asset index created: {index_file}")
        
        # Print summary
        total_assets = sum(len(assets) for assets in index.values())
        logger.info(f"Total assets extracted: {total_assets}")
        for category, assets in index.items():
            if assets:
                logger.info(f"  {category}: {len(assets)} assets")


def find_game_path() -> Optional[str]:
    """Try to find ROTMG Exalt installation"""
    possible_paths = []
    
    # Linux paths
    steam_paths = [
        Path.home() / ".steam/steam/steamapps/common/Realm of the Mad God Exalt/RotMG Exalt_Data",
        Path.home() / ".local/share/Steam/steamapps/common/Realm of the Mad God Exalt/RotMG Exalt_Data"
    ]
    possible_paths.extend(steam_paths)
    
    # Wine/Proton paths
    wine_paths = [
        Path.home() / ".steam/debian-installation/steamapps/compatdata/200210/pfx/drive_c/users/steamuser/Documents/RealmOfTheMadGod/Production/RotMG Exalt_Data",
        Path.home() / ".wine/drive_c/Program Files (x86)/Steam/steamapps/common/Realm of the Mad God Exalt/RotMG Exalt_Data"
    ]
    possible_paths.extend(wine_paths)
    
    for path in possible_paths:
        if path.exists() and (path / "resources.assets").exists():
            logger.info(f"Found ROTMG Exalt at: {path}")
            return str(path)
            
    return None


def main():
    parser = argparse.ArgumentParser(description="Simple ROTMG Asset Extractor")
    parser.add_argument('--game-path', type=str, help='Path to ROTMG Exalt_Data directory')
    parser.add_argument('--output', type=str, default='assets', help='Output directory for extracted assets')
    
    args = parser.parse_args()
    
    try:
        # Create logs directory
        Path('logs').mkdir(exist_ok=True)
        
        # Find or use provided game path
        game_path = args.game_path
        if not game_path:
            game_path = find_game_path()
            if not game_path:
                logger.error("Could not find ROTMG Exalt installation. Please provide --game-path")
                sys.exit(1)
        
        # Initialize extractor
        extractor = SimpleAssetExtractor(game_path, args.output)
        
        # Extract assets
        extractor.extract_assets()
        
        logger.info("Simple asset extraction completed successfully!")
        print(f"\nAssets extracted to: {extractor.output_path}")
        print("You can now use these assets with OpenCV in your bot!")
        
    except Exception as e:
        logger.error(f"Asset extraction failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 