import cv2
import numpy as np
import mss
import math
import json
import os
from pathlib import Path
from vision.asset_loader import AssetLoader
import logging

# Initialize the asset loader and detection pipeline
asset_loader = AssetLoader("assets")
pipeline, matchers = asset_loader.create_detection_pipeline()
logger = logging.getLogger(__name__)

# Load calibration data
calibration_data = {}
def load_calibration():
    """Load calibration data from file"""
    global calibration_data
    calib_file = Path("config/calibration.json")
    if calib_file.exists():
        try:
            with open(calib_file, 'r') as f:
                calibration_data = json.load(f)
            logger.info("Calibration data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load calibration data: {e}")
            calibration_data = {}

# Load calibration on module import
load_calibration()

# Optionally, load item values from a metadata file if available
try:
    import json
    with open("assets/metadata/item_values.json", "r") as f:
        item_values = json.load(f)
except Exception:
    # Fallback to a small hardcoded set
    item_values = {
        "Potion of Life": 5,
        "Potion of Defense": 4,
        "Tincture of Mana": 2,
        "Wooden Sword": 0,
        "Ancient Sword": 3,
    }

# Optionally, build a class icon template set from UI assets
class_templates = {}
for asset in asset_loader.get_ui_assets():
    name = asset['name'].lower()
    if any(cls in name for cls in ["wizard", "warrior", "archer", "priest", "knight", "paladin", "assassin", "necromancer", "huntress", "mystic", "trickster", "sorcerer", "ninja", "samurai", "bard", "summoner"]):
        img = asset_loader.load_image_asset(asset['path'])
        if img is not None:
            class_templates[name] = img


def capture_screen():
    """Capture a screenshot of the RotMG game window (assumes fullscreen 1080p)."""
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # monitor[1] is the first monitor (full screen)
        img = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return frame


def find_enemies(frame):
    """Detect enemies in the frame using all available enemy templates."""
    if 'enemies' not in matchers:
        return []
    
    # Get threshold from calibration or use default
    threshold = calibration_data.get('thresholds', {}).get('template_match', 0.8)
    
    results = []
    matches = matchers['enemies'](frame)
    h, w = frame.shape[0:2]
    for name, locs in matches.items():
        for x, y, tw, th in locs:
            cx = x + tw // 2
            cy = y + th // 2
            dist = math.hypot(cx - w // 2, cy - h // 2)
            results.append({'center': (cx, cy), 'distance': dist, 'name': name})
    return results


def find_bullets(frame):
    """Detect bullets/projectiles in the frame using all available projectile templates."""
    if 'projectiles' not in matchers:
        return []
    
    # Get threshold from calibration or use default
    threshold = calibration_data.get('thresholds', {}).get('template_match', 0.8)
    
    results = []
    matches = matchers['projectiles'](frame)
    for name, locs in matches.items():
        for x, y, tw, th in locs:
            bx = x + tw // 2
            by = y + th // 2
            results.append({'center': (bx, by), 'name': name})
    return results


def find_loot(frame):
    """Detect lootable items or bags on the ground using UI/loot templates."""
    loot_found = []
    # Use UI elements and effects for loot detection
    for category in ['ui_elements', 'effects']:
        if category in matchers:
            matches = matchers[category](frame)
            for name, locs in matches.items():
                for x, y, tw, th in locs:
                    loot_found.append({'name': name, 'center': (x + tw // 2, y + th // 2)})
    return loot_found


def get_hp_percent(frame):
    """Read the player's HP bar from the frame and return percentage (0-100)."""
    # Get HP bar coordinates from calibration data
    hp_config = calibration_data.get('hp_bar', {})
    x1 = hp_config.get('x1', 50)
    y1 = hp_config.get('y1', 900)
    x2 = hp_config.get('x2', 250)
    y2 = hp_config.get('y2', 920)
    
    # Ensure coordinates are within frame bounds
    h, w = frame.shape[:2]
    x1 = max(0, min(x1, w-1))
    y1 = max(0, min(y1, h-1))
    x2 = max(0, min(x2, w-1))
    y2 = max(0, min(y2, h-1))
    
    # Ensure x1 < x2 and y1 < y2
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    
    hp_region = frame[y1:y2, x1:x2]
    if hp_region.size == 0:
        return None
    
    # Convert to HSV and measure red content
    hsv = cv2.cvtColor(hp_region, cv2.COLOR_BGR2HSV)
    
    # Get red threshold from calibration or use default
    red_threshold = calibration_data.get('thresholds', {}).get('hp_red', 150)
    
    # mask for red color (RotMG HP bar is typically red when filled)
    red_lower = np.array([0, red_threshold, 100])
    red_upper = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, red_lower, red_upper)
    
    # Percentage of pixels that are red in the bar region
    red_pixels = cv2.countNonZero(mask)
    total_pixels = hp_region.shape[0] * hp_region.shape[1]
    
    if total_pixels == 0:
        return None
        
    percent = int((red_pixels / total_pixels) * 100)
    return max(0, min(100, percent))


def infer_player_class(frame):
    """Identify player class by looking at equipped weapon/ability icons using UI assets."""
    # Get weapon slot coordinates from calibration or use defaults
    weapon_config = calibration_data.get('weapon_slot', {})
    x1 = weapon_config.get('x1', 50)
    y1 = weapon_config.get('y1', 820)
    x2 = weapon_config.get('x2', 90)
    y2 = weapon_config.get('y2', 860)
    
    # Ensure coordinates are within frame bounds
    h, w = frame.shape[:2]
    x1 = max(0, min(x1, w-1))
    y1 = max(0, min(y1, h-1))
    x2 = max(0, min(x2, w-1))
    y2 = max(0, min(y2, h-1))
    
    weapon_slot = frame[y1:y2, x1:x2]
    if weapon_slot.size == 0:
        return None
        
    gray = cv2.cvtColor(weapon_slot, cv2.COLOR_BGR2GRAY)
    detected_class = None
    best_match = 0.0
    
    # Get threshold from calibration or use default
    threshold = calibration_data.get('thresholds', {}).get('template_match', 0.8)
    
    for cls, tpl in class_templates.items():
        if tpl is None:
            continue
        tpl_gray = cv2.cvtColor(tpl, cv2.COLOR_BGR2GRAY) if len(tpl.shape) == 3 else tpl
        res = cv2.matchTemplate(gray, tpl_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > threshold and max_val > best_match:
            detected_class = cls
            best_match = max_val
    return detected_class


def find_obstacles(frame):
    """Identify obstacles (non-walkable terrain) in the frame for pathfinding."""
    # Use terrain templates to identify non-walkable tiles
    obstacles = []
    if 'terrain' in matchers:
        matches = matchers['terrain'](frame)
        for name, locs in matches.items():
            if any(keyword in name.lower() for keyword in ['wall', 'rock', 'obstacle', 'lava']):
                for x, y, tw, th in locs:
                    obstacles.append({'name': name, 'center': (x + tw // 2, y + th // 2)})
    return obstacles


def inventory_is_full(frame):
    """Check if inventory has no empty slots (by detecting empty slot graphics)."""
    # Get inventory region from calibration or use defaults
    inventory_config = calibration_data.get('inventory_region', {})
    x1 = inventory_config.get('x1', 1600)
    y1 = inventory_config.get('y1', 400)
    x2 = inventory_config.get('x2', 1900)
    y2 = inventory_config.get('y2', 800)
    
    # Ensure coordinates are within frame bounds
    h, w = frame.shape[:2]
    x1 = max(0, min(x1, w-1))
    y1 = max(0, min(y1, h-1))
    x2 = max(0, min(x2, w-1))
    y2 = max(0, min(y2, h-1))
    
    inventory_region = frame[y1:y2, x1:x2]
    if inventory_region.size == 0:
        return False
    
    # Simple heuristic: check if there are many non-black pixels (indicating items)
    gray = cv2.cvtColor(inventory_region, cv2.COLOR_BGR2GRAY)
    non_zero_pixels = cv2.countNonZero(gray)
    total_pixels = gray.shape[0] * gray.shape[1]
    
    if total_pixels == 0:
        return False
        
    # If more than 30% of inventory area has content, assume it's full
    occupancy_ratio = non_zero_pixels / total_pixels
    return occupancy_ratio > 0.3


def find_worst_item_slot(frame):
    """Find the inventory slot (index) containing the worst (lowest value) non-equippable item."""
    # This is a simplified implementation
    # In a real bot, we'd need to identify each inventory item and cross-reference with item_values
    # For now, assume slot 8 (last slot) is the worst
    return 8


def get_item_value(item_name):
    """Lookup the desirability value of an item by name."""
    return item_values.get(item_name, -1)


def is_bullet_dangerous(bullet):
    """Determine if a bullet is on a collision course with the player (simplified)."""
    bx, by = bullet['center']
    
    # Get player position from calibration or assume center
    player_config = calibration_data.get('player_position', {})
    px = player_config.get('x', 960)  # center of 1920x1080
    py = player_config.get('y', 540)
    
    # Get danger radius from calibration or use default
    danger_radius = calibration_data.get('danger_radius', 50)
    
    dist = math.hypot(bx - px, by - py)
    return dist < danger_radius


def get_dodge_direction(bullet):
    """Get a direction (e.g. 'left','right','up','down') to dodge the given bullet."""
    bx, by = bullet['center']
    
    # Get player position from calibration or assume center
    player_config = calibration_data.get('player_position', {})
    px = player_config.get('x', 960)
    py = player_config.get('y', 540)
    
    if abs(bx - px) > abs(by - py):
        return 'up' if by < py else 'down'
    else:
        return 'left' if bx < px else 'right'


def reload_calibration():
    """Reload calibration data from file (useful for runtime updates)"""
    load_calibration()
    logger.info("Calibration data reloaded")


def get_calibration_status():
    """Get current calibration status and statistics"""
    status = {
        'loaded': len(calibration_data) > 0,
        'hp_bar_configured': 'hp_bar' in calibration_data,
        'thresholds_configured': 'thresholds' in calibration_data,
        'features_enabled': calibration_data.get('detection_features', {}),
        'total_settings': len(calibration_data)
    }
    return status
