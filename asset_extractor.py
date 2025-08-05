#!/usr/bin/env python3
"""
ROTMG Asset Extractor
Extracts game assets from local ROTMG Exalt files for bot use with OpenCV
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse

# Add exalt-extractor to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'exalt-extractor'))

try:
    from utils import Resources, UnityExtractor, Logger
    from utils.Files import assert_path_exists
    from assets import Texture2D, TextAsset, GameObject, MonoBehaviour
except ImportError as e:
    print(f"Error importing exalt-extractor modules: {e}")
    print("Please ensure exalt-extractor is properly installed and configured")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/asset_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ROTMGAssetExtractor:
    """Extracts and organizes ROTMG assets for bot use"""
    
    def __init__(self, game_path: Optional[str] = None, output_path: str = "assets"):
        self.game_path = game_path
        self.output_path = Path(output_path)
        self.resources = None
        self.extractor = None
        
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
    
    def find_game_path(self) -> str:
        """Automatically find ROTMG Exalt installation path"""
        possible_paths = []
        
        # Windows paths
        if os.name == 'nt':
            user_docs = Path.home() / "Documents" / "RealmOfTheMadGod" / "Production" / "RotMG Exalt_Data"
            possible_paths.append(user_docs)
            
            # Steam installation
            steam_paths = [
                Path("C:/Program Files (x86)/Steam/steamapps/common/Realm of the Mad God Exalt/RotMG Exalt_Data"),
                Path("C:/Program Files/Steam/steamapps/common/Realm of the Mad God Exalt/RotMG Exalt_Data")
            ]
            possible_paths.extend(steam_paths)
            
        # Linux paths
        else:
            # Steam on Linux
            steam_paths = [
                Path.home() / ".steam/steam/steamapps/common/Realm of the Mad God Exalt/RotMG Exalt_Data",
                Path.home() / ".local/share/Steam/steamapps/common/Realm of the Mad God Exalt/RotMG Exalt_Data"
            ]
            possible_paths.extend(steam_paths)
            
            # Wine/Proton
            wine_paths = [
                Path.home() / ".wine/drive_c/Program Files (x86)/Steam/steamapps/common/Realm of the Mad God Exalt/RotMG Exalt_Data",
                Path.home() / ".wine/drive_c/Program Files/Steam/steamapps/common/Realm of the Mad God Exalt/RotMG Exalt_Data"
            ]
            possible_paths.extend(wine_paths)
        
        for path in possible_paths:
            if path.exists() and (path / "resources.assets").exists():
                logger.info(f"Found ROTMG Exalt at: {path}")
                return str(path)
                
        raise FileNotFoundError(
            "Could not automatically find ROTMG Exalt installation. "
            "Please provide the path manually using --game-path"
        )
    
    def initialize_extractor(self):
        """Initialize the Unity asset extractor"""
        if not self.game_path:
            self.game_path = self.find_game_path()
            
        logger.info(f"Initializing extractor with game path: {self.game_path}")
        
        try:
            self.resources = Resources(self.game_path)
            self.extractor = UnityExtractor(self.resources, str(self.output_path))
            logger.info("Extractor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize extractor: {e}")
            raise
    
    def extract_all_assets(self):
        """Extract all relevant assets for bot use"""
        if not self.extractor:
            self.initialize_extractor()
            
        logger.info("Starting asset extraction...")
        
        # Extract spritesheets and metadata
        self.extract_spritesheets()
        self.extract_metadata()
        self.extract_textures()
        self.extract_game_objects()
        
        logger.info("Asset extraction completed!")
    
    def extract_spritesheets(self):
        """Extract spritesheets and organize by type"""
        logger.info("Extracting spritesheets...")
        
        try:
            # Extract using the existing extractor
            self.extractor.extract_spritesheets(create_actionscript=False)
            
            # Move spritesheet.json to metadata folder
            spritesheet_json = self.output_path / "spritesheets" / "spritesheet.json"
            if spritesheet_json.exists():
                shutil.move(str(spritesheet_json), str(self.output_path / "metadata" / "spritesheet.json"))
                
            # Parse spritesheet to categorize sprites
            self._categorize_sprites()
            
        except Exception as e:
            logger.error(f"Error extracting spritesheets: {e}")
    
    def extract_metadata(self):
        """Extract game metadata files"""
        logger.info("Extracting metadata...")
        
        try:
            # Extract manifests
            self.extractor.extract_manifests()
            
            # Move manifest files to metadata folder
            for manifest_file in ["assets_manifest.json", "assets_manifest.xml"]:
                src = self.output_path / manifest_file
                dst = self.output_path / "metadata" / manifest_file
                if src.exists():
                    shutil.move(str(src), str(dst))
                    
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
    
    def extract_textures(self):
        """Extract and organize texture assets"""
        logger.info("Extracting textures...")
        
        try:
            # Extract all Texture2D assets
            self.extractor.extract_texture2d()
            
            # Organize textures by type
            self._organize_textures()
            
        except Exception as e:
            logger.error(f"Error extracting textures: {e}")
    
    def extract_game_objects(self):
        """Extract game object data"""
        logger.info("Extracting game objects...")
        
        try:
            # Extract XML data
            self.extractor.extract_xml(create_actionscript=False)
            
            # Move XML files to metadata folder
            xml_dir = self.output_path / "xml"
            if xml_dir.exists():
                for xml_file in xml_dir.glob("*.xml"):
                    shutil.move(str(xml_file), str(self.output_path / "metadata" / xml_file.name))
                xml_dir.rmdir()
                
        except Exception as e:
            logger.error(f"Error extracting game objects: {e}")
    
    def _categorize_sprites(self):
        """Categorize sprites from spritesheet.json into appropriate folders"""
        spritesheet_path = self.output_path / "metadata" / "spritesheet.json"
        
        if not spritesheet_path.exists():
            logger.warning("spritesheet.json not found, skipping categorization")
            return
            
        try:
            with open(spritesheet_path, 'r') as f:
                spritesheet_data = json.load(f)
            
            # Define categorization rules
            categories = {
                'enemies': ['enemy', 'monster', 'boss', 'creature'],
                'projectiles': ['projectile', 'bullet', 'shot', 'spell'],
                'terrain': ['tile', 'ground', 'wall', 'floor', 'terrain'],
                'ui': ['ui', 'button', 'icon', 'interface'],
                'effects': ['effect', 'particle', 'animation']
            }
            
            # Process each sprite
            for sprite_name, sprite_data in spritesheet_data.items():
                category = self._determine_sprite_category(sprite_name, categories)
                
                # Create sprite info file
                sprite_info = {
                    'name': sprite_name,
                    'category': category,
                    'data': sprite_data
                }
                
                sprite_file = self.output_path / category / f"{sprite_name}.json"
                with open(sprite_file, 'w') as f:
                    json.dump(sprite_info, f, indent=2)
                    
            logger.info("Sprite categorization completed")
            
        except Exception as e:
            logger.error(f"Error categorizing sprites: {e}")
    
    def _determine_sprite_category(self, sprite_name: str, categories: Dict[str, List[str]]) -> str:
        """Determine which category a sprite belongs to based on its name"""
        sprite_lower = sprite_name.lower()
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in sprite_lower:
                    return category
        
        # Default to terrain if no match found
        return 'terrain'
    
    def _organize_textures(self):
        """Organize extracted texture files"""
        texture_dir = self.output_path / "texture2d"
        
        if not texture_dir.exists():
            return
            
        # Move texture files to appropriate categories
        for texture_file in texture_dir.glob("*.png"):
            category = self._determine_sprite_category(texture_file.stem, {
                'enemies': ['enemy', 'monster', 'boss'],
                'projectiles': ['projectile', 'bullet'],
                'terrain': ['tile', 'ground'],
                'ui': ['ui', 'button'],
                'effects': ['effect', 'particle']
            })
            
            dst = self.output_path / category / texture_file.name
            shutil.move(str(texture_file), str(dst))
            
        # Remove empty texture directory
        if texture_dir.exists() and not any(texture_dir.iterdir()):
            texture_dir.rmdir()
    
    def create_asset_index(self):
        """Create an index file for easy asset lookup"""
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
                            'type': file_path.suffix[1:]  # Remove the dot
                        })
        
        # Save index
        index_file = self.output_path / "asset_index.json"
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
            
        logger.info(f"Asset index created: {index_file}")
    
    def cleanup(self):
        """Clean up temporary files and directories"""
        logger.info("Cleaning up...")
        
        # Remove empty directories
        for item in self.output_path.iterdir():
            if item.is_dir() and not any(item.iterdir()):
                item.rmdir()
                logger.info(f"Removed empty directory: {item}")


def main():
    parser = argparse.ArgumentParser(description="Extract ROTMG assets for bot use")
    parser.add_argument('--game-path', type=str, help='Path to ROTMG Exalt_Data directory')
    parser.add_argument('--output', type=str, default='assets', help='Output directory for extracted assets')
    parser.add_argument('--cleanup', action='store_true', help='Clean up temporary files after extraction')
    
    args = parser.parse_args()
    
    try:
        # Create logs directory
        Path('logs').mkdir(exist_ok=True)
        
        # Initialize extractor
        extractor = ROTMGAssetExtractor(
            game_path=args.game_path,
            output_path=args.output
        )
        
        # Extract assets
        extractor.extract_all_assets()
        
        # Create asset index
        extractor.create_asset_index()
        
        # Cleanup if requested
        if args.cleanup:
            extractor.cleanup()
            
        logger.info("Asset extraction completed successfully!")
        print(f"\nAssets extracted to: {extractor.output_path}")
        print("You can now use these assets with OpenCV in your bot!")
        
    except Exception as e:
        logger.error(f"Asset extraction failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 