import cv2
import numpy as np
import mss
import math
from vision.asset_loader import AssetLoader
import logging

# Initialize the asset loader and detection pipeline
asset_loader = AssetLoader("assets")
pipeline, matchers = asset_loader.create_detection_pipeline()
logger = logging.getLogger(__name__)

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
    # Load config to get HP bar region
    try:
        from config import settings
        config = settings.load_config()
        hp_config = config.get('hp_bar_region', {'x': 50, 'y': 900, 'width': 200, 'height': 20})
        
        x = hp_config['x']
        y = hp_config['y']
        width = hp_config['width']
        height = hp_config['height']
        
        hp_region = frame[y:y+height, x:x+width]
    except Exception as e:
        logger.warning(f"Failed to load HP config, using defaults: {e}")
        # Fallback to hardcoded values
        hp_region = frame[900:920, 50:250]
    
    if hp_region.size == 0:
        return None
    # Convert to HSV and measure red content
    hsv = cv2.cvtColor(hp_region, cv2.COLOR_BGR2HSV)
    # mask for red color (RotMG HP bar is typically red when filled)
    red_lower = np.array([0, 150, 100])
    red_upper = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, red_lower, red_upper)
    # Percentage of pixels that are red in the bar region
    red_pixels = cv2.countNonZero(mask)
    total_pixels = hp_region.shape[0] * hp_region.shape[1]
    percent = int((red_pixels / total_pixels) * 100)
    return max(0, min(100, percent))


def infer_player_class(frame):
    """Identify player class by looking at equipped weapon/ability icons using UI assets."""
    # Assume the equipment UI is always at a fixed position (e.g., top-left or bottom).
    # For simplicity, check a small region where the weapon icon is shown.
    weapon_slot = frame[820:860, 50:90]  # hypothetical coordinates
    gray = cv2.cvtColor(weapon_slot, cv2.COLOR_BGR2GRAY)
    detected_class = None
    best_match = 0.0
    for cls, tpl in class_templates.items():
        if tpl is None:
            continue
        tpl_gray = cv2.cvtColor(tpl, cv2.COLOR_BGR2GRAY) if len(tpl.shape) == 3 else tpl
        res = cv2.matchTemplate(gray, tpl_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > 0.8 and max_val > best_match:
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
    # If the game has a specific icon or color for empty slots, detect that.
    # For example, empty slot might be a dark gray square of a certain size.
    # We would search the inventory UI region for that template.
    # (Optional: Use UI templates for empty slot detection)
    return False  # stub implementation (would need UI specifics)


def find_worst_item_slot(frame):
    """Find the inventory slot (index) containing the worst (lowest value) non-equippable item."""
    # In a real bot, we'd need to identify each inventory item and cross-reference with item_values.
    # For simplicity, assume slot 8 (last slot) is the worst. 
    return 8  # e.g., drop the item in the last slot of inventory


def get_item_value(item_name):
    """Lookup the desirability value of an item by name."""
    return item_values.get(item_name, -1)


def is_bullet_dangerous(bullet):
    """Determine if a bullet is on a collision course with the player (simplified)."""
    bx, by = bullet['center']
    px, py = 960, 540  # center of 1920x1080
    dist = math.hypot(bx - px, by - py)
    return dist < 50  # if a bullet is extremely close to player


def get_dodge_direction(bullet):
    """Get a direction (e.g. 'left','right','up','down') to dodge the given bullet."""
    bx, by = bullet['center']
    px, py = 960, 540  # player at center
    if abs(bx - px) > abs(by - py):
        return 'up' if by < py else 'down'
    else:
        return 'left' if bx < px else 'right'
