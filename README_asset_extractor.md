# ROTMG Asset Extractor

This tool extracts game assets from Realm of the Mad God Exalt local files and organizes them for use with OpenCV-based bot detection.

## Features

- **Automatic Game Detection**: Automatically finds ROTMG Exalt installation on Windows and Linux
- **Comprehensive Asset Extraction**: Extracts sprites, textures, metadata, and game objects
- **Organized Output**: Categorizes assets into enemies, projectiles, terrain, UI, and effects
- **OpenCV Integration**: Assets are ready for use with OpenCV template matching
- **Asset Indexing**: Creates searchable index of all extracted assets

## Prerequisites

- Python 3.8 or higher
- ROTMG Exalt installed on your system
- pip3 package manager

## Installation

1. **Clone or download this repository**
   ```bash
   # If you have the repository
   cd RotMG_bot
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup_asset_extractor.sh
   ./setup_asset_extractor.sh
   ```

3. **Activate the virtual environment**
   ```bash
   source venv/bin/activate
   ```

## Usage

### Basic Extraction

```bash
# Activate virtual environment
source venv/bin/activate

# Run extraction (auto-detects game path)
python3 asset_extractor.py
```

### Custom Game Path

If the automatic detection doesn't work, specify the game path manually:

```bash
python3 asset_extractor.py --game-path "/path/to/RotMG Exalt_Data"
```

### Custom Output Directory

```bash
python3 asset_extractor.py --output "my_assets"
```

### Cleanup After Extraction

```bash
python3 asset_extractor.py --cleanup
```

## Output Structure

After extraction, your `assets/` folder will contain:

```
assets/
├── enemies/           # Enemy sprites and textures
├── projectiles/       # Projectile sprites
├── terrain/          # Terrain tiles and objects
├── ui/               # UI elements and buttons
├── effects/          # Visual effects and particles
├── metadata/         # Game metadata and spritesheet data
├── spritesheets/     # Original spritesheet images
└── asset_index.json  # Searchable index of all assets
```

## Using Assets with OpenCV

The `vision/asset_loader.py` module provides easy integration with OpenCV:

```python
from vision.asset_loader import AssetLoader

# Initialize asset loader
loader = AssetLoader("assets")

# Load enemy assets
enemies = loader.get_enemy_assets()
enemy_images = loader.load_asset_images('enemies')

# Create template matcher for enemies
enemy_matcher = loader.create_multi_template_matcher(
    list(enemy_images.keys()), 
    category='enemies'
)

# Use with screen capture
import cv2
screen = cv2.imread('screen_capture.png')
detected_enemies = enemy_matcher(screen)

# Get dangerous terrain for navigation
dangerous_assets = loader.get_damage_indicators()
safe_assets = loader.get_navigation_assets()
```

## Common Game Paths

### Windows
- **Steam**: `C:\Program Files (x86)\Steam\steamapps\common\Realm of the Mad God Exalt\RotMG Exalt_Data`
- **Documents**: `C:\Users\[Username]\Documents\RealmOfTheMadGod\Production\RotMG Exalt_Data`

### Linux
- **Steam**: `~/.steam/steam/steamapps/common/Realm of the Mad God Exalt/RotMG Exalt_Data`
- **Wine**: `~/.wine/drive_c/Program Files (x86)/Steam/steamapps/common/Realm of the Mad God Exalt/RotMG Exalt_Data`

## Troubleshooting

### "Could not automatically find ROTMG Exalt installation"

1. Make sure ROTMG Exalt is installed
2. Provide the path manually using `--game-path`
3. Check that the path contains `resources.assets` file

### Import Errors

1. Ensure you've run the setup script
2. Activate the virtual environment: `source venv/bin/activate`
3. Install dependencies manually: `pip install -r requirements_asset_extractor.txt`

### Permission Errors

1. Make sure you have read access to the game files
2. Run with appropriate permissions
3. Check that the output directory is writable

### Empty Asset Categories

This is normal if certain asset types aren't found in your game files. The extractor will create empty directories and continue with available assets.

## Integration with Bot

The extracted assets are designed to work seamlessly with your ROTMG bot:

1. **Detection**: Use template matching to identify enemies, projectiles, and terrain
2. **Navigation**: Identify safe paths and avoid dangerous terrain
3. **Combat**: Recognize enemy types and projectile patterns
4. **UI Interaction**: Detect UI elements for menu navigation

## File Descriptions

- `asset_extractor.py`: Main extraction script
- `vision/asset_loader.py`: OpenCV integration module
- `setup_asset_extractor.sh`: Installation script
- `requirements_asset_extractor.txt`: Python dependencies
- `README_asset_extractor.md`: This documentation

## Support

If you encounter issues:

1. Check the logs in `logs/asset_extraction.log`
2. Ensure all dependencies are installed
3. Verify your game installation path
4. Check that you have sufficient disk space for extraction

## License

This tool is provided as-is for educational and personal use. Please respect the terms of service for ROTMG Exalt. 