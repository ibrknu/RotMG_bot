import time
import math
import logging
import subprocess
import re
from PySide6.QtCore import QObject, Signal
import mss
import numpy as np
import cv2

from vision import detection
from input import keyboard, mouse

class RotMGbotLinux(QObject):
    """Linux-compatible bot logic for RotMG running through Proton"""
    # Signal to send status messages to GUI
    status_signal = Signal(str)

    def __init__(self, config):
        super().__init__()
        # Load config parameters
        self.auto_nexus_percent = config.get('auto_nexus_percent', 30)
        self.movement_mode = config.get('movement_mode', 'Kiting')
        self.player_class = config.get('player_class', 'Wizard')
        self.keybinds = config.get('keybinds', {})
        
        # Internal state
        self._running = False
        self.inventory_full = False
        
        # Initialize input controllers
        self.keyboard = keyboard.Controller()
        self.mouse = mouse.Controller()
        self.user_input_monitor = keyboard.Listener(on_press=self.on_user_key)
        self.user_input_monitor.start()
        
        # Linux-specific window management
        self.rotmg_window_info = None
        self.game_region = None
        
        # Initialize window detection
        self.find_rotmg_window()
        
        logging.info("Linux RotMG Bot initialized with auto_nexus_percent=%d, movement_mode=%s" % 
                     (self.auto_nexus_percent, self.movement_mode))

    def find_rotmg_window(self):
        """Find RotMG window using Linux window managers"""
        try:
            # Try to find window using xdotool
            result = subprocess.run(['xdotool', 'search', '--name', 'RotMG'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                window_ids = result.stdout.strip().split('\n')
                if window_ids and window_ids[0]:
                    self.rotmg_window_info = {
                        'id': window_ids[0],
                        'name': 'RotMG'
                    }
                    self.update_game_region()
                    logging.info(f"Found RotMG window: {self.rotmg_window_info}")
                    return True
            
            # Try alternative window names for Proton
            proton_names = [
                'Realm of the Mad God',
                'Realm',
                'RotMG - Realm of the Mad God',
                'RotMG Exalt',
                'Realm of the Mad God Exalt',
                'Steam - Realm of the Mad God'
            ]
            
            for name in proton_names:
                result = subprocess.run(['xdotool', 'search', '--name', name], 
                                      capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    window_ids = result.stdout.strip().split('\n')
                    if window_ids and window_ids[0]:
                        self.rotmg_window_info = {
                            'id': window_ids[0],
                            'name': name
                        }
                        self.update_game_region()
                        logging.info(f"Found RotMG window: {self.rotmg_window_info}")
                        return True
            
            # If no window found, assume fullscreen
            logging.warning("RotMG window not found, assuming fullscreen mode")
            return False
            
        except FileNotFoundError:
            logging.warning("xdotool not found, assuming fullscreen mode")
            return False
        except Exception as e:
            logging.error(f"Error finding RotMG window: {e}")
            return False

    def update_game_region(self):
        """Update the game region for screen capture"""
        if not self.rotmg_window_info:
            # Use full screen
            self.game_region = None
            return
            
        try:
            # Get window geometry using xdotool
            result = subprocess.run(['xdotool', 'getwindowgeometry', self.rotmg_window_info['id']], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # Parse output like "Window 1234\n  Position: 100,200\n  Size: 1920x1080"
                lines = result.stdout.strip().split('\n')
                x, y, width, height = None, None, None, None
                
                for line in lines:
                    if 'Position:' in line:
                        pos_match = re.search(r'Position: (\d+),(\d+)', line)
                        if pos_match:
                            x, y = int(pos_match.group(1)), int(pos_match.group(2))
                    elif 'Size:' in line:
                        size_match = re.search(r'Size: (\d+)x(\d+)', line)
                        if size_match:
                            width, height = int(size_match.group(1)), int(size_match.group(2))
                
                # Only set game region if we have all coordinates
                if all(v is not None for v in [x, y, width, height]):
                    self.game_region = {
                        'left': x,
                        'top': y,
                        'width': width,
                        'height': height
                    }
                    logging.info(f"Game region: {self.game_region}")
                else:
                    logging.warning("Could not parse complete window geometry, using fullscreen")
                    self.game_region = None
            else:
                logging.warning("Failed to get window geometry, using fullscreen")
                self.game_region = None
                            
        except Exception as e:
            logging.error(f"Error getting window geometry: {e}")
            self.game_region = None

    def focus_game_window(self):
        """Focus the RotMG window"""
        if not self.rotmg_window_info:
            return False
            
        try:
            subprocess.run(['xdotool', 'windowactivate', self.rotmg_window_info['id']], 
                         capture_output=True)
            time.sleep(0.1)  # Small delay for window focus
            return True
        except Exception as e:
            logging.error(f"Error focusing window: {e}")
            return False

    def capture_game_screen(self):
        """Capture screen of the game window or full screen"""
        try:
            with mss.mss() as sct:
                # Always try full screen first as fallback
                if self.game_region and all(k in self.game_region for k in ['left', 'top', 'width', 'height']):
                    # Validate coordinates
                    if (self.game_region['left'] >= 0 and self.game_region['top'] >= 0 and 
                        self.game_region['width'] > 0 and self.game_region['height'] > 0):
                        try:
                            # Capture specific game window
                            monitor = self.game_region
                            img = np.array(sct.grab(monitor))
                            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                            return frame
                        except Exception as window_capture_error:
                            logging.warning(f"Window capture failed, falling back to fullscreen: {window_capture_error}")
                
                # Fallback to full screen capture
                monitor = sct.monitors[1]  # Primary monitor
                img = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                return frame
                
        except Exception as e:
            logging.error(f"Screen capture error: {e}")
            return None

    def on_user_key(self, key):
        """Callback for user key press events"""
        try:
            k = key.char.lower()
        except AttributeError:
            k = str(key)
        
        # Emergency stop with Ctrl+Q
        if hasattr(key, 'ctrl') and key.ctrl and k == 'q':
            logging.info("User pressed Ctrl+Q, stopping bot.")
            self.status_signal.emit("User pressed Ctrl+Q, stopping bot.")
            self._running = False

    def stop(self):
        """Signal the bot loop to stop gracefully."""
        self._running = False

    def run(self):
        """Main bot loop optimized for Linux/Proton"""
        logging.info("Linux RotMG Bot started.")
        self.status_signal.emit("Linux RotMG Bot started - beginning main loop...")
        self._running = True

        # Focus game window if found
        if self.rotmg_window_info:
            self.focus_game_window()
            self.status_signal.emit(f"Focused game window: {self.rotmg_window_info['name']}")
        else:
            self.status_signal.emit("Running in fullscreen mode")

        # Main loop
        prev_time = time.time()
        loop_count = 0
        consecutive_failures = 0
        max_failures = 10  # Stop after 10 consecutive failures
        
        while self._running:
            try:
                loop_start = time.time()
                loop_count += 1
                
                # Log every 60 loops (about once per second)
                if loop_count % 60 == 0:
                    self.status_signal.emit(f"Bot running - loop {loop_count}")
                
                # 1. Screen capture with timeout
                frame = None
                try:
                    frame = self.capture_game_screen()
                    if frame is not None:
                        consecutive_failures = 0  # Reset failure counter on success
                    else:
                        consecutive_failures += 1
                        self.status_signal.emit(f"Screen capture failed (attempt {consecutive_failures})")
                        if consecutive_failures >= max_failures:
                            self.status_signal.emit("Too many capture failures, stopping bot")
                            break
                        time.sleep(0.1)
                        continue
                except Exception as e:
                    consecutive_failures += 1
                    self.status_signal.emit(f"Screen capture error: {e}")
                    if consecutive_failures >= max_failures:
                        self.status_signal.emit("Too many capture errors, stopping bot")
                        break
                    time.sleep(0.1)
                    continue

                # 2. Vision: detect game elements (with timeout protection)
                try:
                    player_hp = detection.get_hp_percent(frame)
                    enemies = detection.find_enemies(frame)
                    bullets = detection.find_bullets(frame)
                    loot_items = detection.find_loot(frame)
                    obstacles = detection.find_obstacles(frame)
                    
                    if detection.inventory_is_full(frame):
                        self.inventory_full = True
                    else:
                        self.inventory_full = False
                    
                    # Log detection results occasionally
                    if loop_count % 120 == 0:  # Every 2 seconds
                        self.status_signal.emit(f"Detection: HP={player_hp}%, Enemies={len(enemies)}, Bullets={len(bullets)}")
                        
                except Exception as e:
                    self.status_signal.emit(f"Detection failed: {e}")
                    time.sleep(0.1)
                    continue

                # 3. Decision Making:
                # Auto-Nexus: if HP below threshold, trigger Nexus
                if player_hp is not None and player_hp <= self.auto_nexus_percent:
                    logging.warning(f"HP {player_hp}% <= threshold! Auto-Nexus activated.")
                    self.status_signal.emit("Auto-Nexus triggered! HP low.")
                    # Press the Nexus key (teleport to Nexus)
                    nexus_key = self.keybinds.get('nexus', 'r')
                    self.keyboard.tap_key(nexus_key)
                    time.sleep(1)  # small delay after nexusing
                    self._running = False
                    continue

                # Combat logic (simplified to prevent freezing)
                if enemies and len(enemies) > 0:
                    target = enemies[0]  # take first enemy
                    if 'center' in target:
                        ex, ey = target['center']
                        
                        # Aim at enemy
                        self.mouse.move_to(ex, ey)
                        # Attack
                        self.mouse.click(button='left')
                        self.status_signal.emit(f"Enemy detected at {target['center']}, attacking.")
                        
                        # Movement based on mode (simplified)
                        if self.movement_mode.lower().startswith("kit"):  # Kiting
                            if 'distance' in target and target['distance'] < 100:  # if enemy too close
                                # Move away from enemy
                                dx = target['center'][0] - frame.shape[1]//2
                                dy = target['center'][1] - frame.shape[0]//2
                                move_x, move_y = -dx, -dy
                                keyboard.move_towards(move_x, move_y, self.keyboard, self.keybinds)
                            else:
                                keyboard.release_movement_keys(self.keyboard, self.keybinds)
                        else:
                            # Circle-Strafe
                            dx = target['center'][0] - frame.shape[1]//2
                            dy = target['center'][1] - frame.shape[0]//2
                            perp_x, perp_y = -dy, dx
                            keyboard.move_towards(perp_x, perp_y, self.keyboard, self.keybinds)
                else:
                    # No enemies seen, stop moving/attacking
                    keyboard.release_movement_keys(self.keyboard, self.keybinds)
                
                # Bullet dodging (simplified)
                if bullets and len(bullets) > 0:
                    for b in bullets[:3]:  # Limit to first 3 bullets to prevent freezing
                        if 'center' in b and detection.is_bullet_dangerous(b):
                            dodge_dir = detection.get_dodge_direction(b)
                            keyboard.move_direction(dodge_dir, self.keyboard, self.keybinds, duration=0.1)
                            self.status_signal.emit("Dodging projectile!")
                            break  # Only dodge one bullet per loop

                # Looting logic (simplified)
                if loot_items and len(loot_items) > 0:
                    if self.inventory_full:
                        worst_slot = detection.find_worst_item_slot(frame)
                        if worst_slot is not None:
                            logging.info(f"Inventory full. Dropping item in slot {worst_slot}.")
                            self.status_signal.emit("Inventory full; dropping least valuable item.")
                            mouse.drop_item(worst_slot, self.mouse, self.keybinds)
                            time.sleep(0.5)
                            self.inventory_full = False
                    
                    # Pick up first desired loot item
                    for item in loot_items[:2]:  # Limit to first 2 items
                        if 'name' in item and 'center' in item:
                            item_name = item['name']
                            value = detection.get_item_value(item_name)
                            if value and value >= 0:
                                ix, iy = item['center']
                                self.mouse.move_to(ix, iy)
                                self.mouse.click(button='left')
                                logging.info(f"Picking up loot: {item_name} at {item['center']}")
                                self.status_signal.emit(f"Looting item: {item_name}")
                                time.sleep(0.2)
                                break

                # 4. Maintain loop timing ~30 FPS (reduced from 60 to prevent freezing)
                loop_end = time.time()
                elapsed = loop_end - loop_start
                if elapsed < 1/30:
                    time.sleep(1/30 - elapsed)
                    
            except Exception as e:
                logging.error(f"Error in main bot loop: {e}")
                self.status_signal.emit(f"Bot loop error: {e}")
                time.sleep(0.5)  # Wait before retrying
                continue

        logging.info("Linux RotMG Bot loop terminated.")
        self.status_signal.emit("Bot stopped.")
        # Ensure movement keys released when stopping
        keyboard.release_movement_keys(self.keyboard, self.keybinds)
        # Stop listening to user input
        self.user_input_monitor.stop() 