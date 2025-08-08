import time
import math
import logging
import numpy as np
import cv2
import mss
from PySide6.QtCore import QObject, Signal
import win32gui
import win32con

from input import keyboard, mouse

class RotMGbot(QObject):
    """Core bot logic running in a separate thread. Performs vision, decision-making, and input control."""
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
        # Guard against accidental nexus on noisy reads
        self._low_hp_consecutive_count = 0
        
        # RotMG window detection
        self.rotmg_window_handle = None
        self.rotmg_window_rect = None
        self.find_rotmg_window()
        
        # Initialize user input monitoring
        self.user_input_monitor = keyboard.Listener(on_press=self.on_user_key)
        self.user_input_monitor.start()
        
        logging.info(f"Bot initialized with auto_nexus_percent={self.auto_nexus_percent}, movement_mode={self.movement_mode}")

    def find_rotmg_window(self):
        """Find the RotMG window by its title."""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                # Look for common RotMG window titles
                rotmg_titles = [
                    "RotMG", "Realm of the Mad God", "Realm", 
                    "RotMG - Realm of the Mad God", "RotMG Exalt",
                    "Realm of the Mad God Exalt"
                ]
                
                for title in rotmg_titles:
                    if title.lower() in window_title.lower():
                        windows.append((hwnd, window_title))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        if windows:
            self.rotmg_window_handle = windows[0][0]
            window_title = windows[0][1]
            self.rotmg_window_rect = win32gui.GetWindowRect(self.rotmg_window_handle)
            self.status_signal.emit(f"Found RotMG window: '{window_title}' at {self.rotmg_window_rect}")
            logging.info(f"Found RotMG window: '{window_title}' at {self.rotmg_window_rect}")
        else:
            self.status_signal.emit("RotMG window not found. Will capture full screen.")
            logging.warning("RotMG window not found, will use full screen capture")
            self.rotmg_window_handle = None
            self.rotmg_window_rect = None

    def capture_rotmg_window(self):
        """Capture specifically the RotMG window."""
        try:
            if self.rotmg_window_handle and self.rotmg_window_rect:
                # Check if window still exists
                if not win32gui.IsWindow(self.rotmg_window_handle):
                    self.find_rotmg_window()
                    if not self.rotmg_window_handle:
                        return None
                
                # Get current window position
                rect = win32gui.GetWindowRect(self.rotmg_window_handle)
                x, y, w, h = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
                
                # Create a new mss instance for this thread to avoid threading issues
                with mss.mss() as sct:
                    # Capture the specific window region
                    monitor = {"top": y, "left": x, "width": w, "height": h}
                    img = np.array(sct.grab(monitor))
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    return frame
            else:
                # Fallback to full screen if RotMG window not found
                with mss.mss() as sct:
                    monitor = sct.monitors[1]  # Primary monitor
                    img = np.array(sct.grab(monitor))
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    return frame
                
        except Exception as e:
            self.status_signal.emit(f"Window capture failed: {e}")
            logging.error(f"Window capture error: {e}")
            return None

    def focus_rotmg_window(self):
        """Bring RotMG window to front and focus it."""
        if self.rotmg_window_handle:
            try:
                # Show window if minimized
                if win32gui.IsIconic(self.rotmg_window_handle):
                    win32gui.ShowWindow(self.rotmg_window_handle, win32con.SW_RESTORE)
                
                # Bring window to front
                win32gui.SetForegroundWindow(self.rotmg_window_handle)
                win32gui.BringWindowToTop(self.rotmg_window_handle)
                
                # Small delay to ensure window is focused
                time.sleep(0.1)
                return True
            except Exception as e:
                self.status_signal.emit(f"Failed to focus RotMG window: {e}")
                return False
        return False

    def on_user_key(self, key):
        """Callback for user key press events. If user presses Ctrl+Q, stop bot."""
        try:
            k = key.char.lower()
        except AttributeError:
            k = str(key)
        
        # Stop bot with Ctrl+Q
        if hasattr(key, 'ctrl') and key.ctrl and k == 'q':
            logging.info("User pressed Ctrl+Q, stopping bot.")
            self.status_signal.emit("User pressed Ctrl+Q, stopping bot.")
            self._running = False

    def stop(self):
        """Signal the bot loop to stop gracefully."""
        self._running = False

    def capture_screen(self):
        """Capture a screenshot of the RotMG window."""
        return self.capture_rotmg_window()

    def get_hp_percent(self, frame):
        """Read the player's HP using the configured HP bar region.
        Returns a percentage 0-100 or None when confidence is insufficient.
        """
        try:
            # Prefer user-configured region
            try:
                from config import settings
                cfg = settings.load_config()
                hp_cfg = cfg.get('hp_bar_region', None)
            except Exception:
                hp_cfg = None

            if hp_cfg:
                x = int(hp_cfg.get('x', 50))
                y = int(hp_cfg.get('y', 900))
                w = int(hp_cfg.get('width', 200))
                h = int(hp_cfg.get('height', 20))
                hp_region = frame[y:y+h, x:x+w]
                regions = [(0, hp_region)] if hp_region.size > 0 else []
            else:
                # Fallback heuristic regions (right sidebar)
                h_frame, w_frame = frame.shape[:2]
                regions = [
                    (0, frame[60:90, w_frame-350:w_frame-50]),
                    (1, frame[80:110, w_frame-350:w_frame-50]),
                    (2, frame[100:130, w_frame-350:w_frame-50]),
                    (3, frame[70:100, w_frame-400:w_frame-50]),
                ]

            best_hp_percent = -1.0
            best_method = "unknown"

            for i, hp_bar_region in regions:
                if hp_bar_region.size == 0:
                    continue

                # Color-based cue (green text density)
                hsv = cv2.cvtColor(hp_bar_region, cv2.COLOR_BGR2HSV)
                bright_green_lower = np.array([40, 150, 150])
                bright_green_upper = np.array([80, 255, 255])
                mask = cv2.inRange(hsv, bright_green_lower, bright_green_upper)
                green_pixels = cv2.countNonZero(mask)
                total_pixels = mask.size
                green_density = (green_pixels / max(1, total_pixels)) * 100.0

                # Optional OCR when available
                try:
                    import pytesseract
                    from PIL import Image
                    gray = cv2.cvtColor(hp_bar_region, cv2.COLOR_BGR2GRAY)
                    gray = cv2.convertScaleAbs(gray, alpha=2.0, beta=0)
                    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
                    kernel = np.ones((1, 1), np.uint8)
                    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                    thresh = cv2.resize(thresh, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
                    pil = Image.fromarray(thresh)
                    txt = pytesseract.image_to_string(
                        pil,
                        config='--psm 7 -c tessedit_char_whitelist=0123456789/()+-'
                    ).strip().replace('\n', '').replace(' ', '')
                    import re
                    m = re.search(r'(\d+)/(\d+)', txt)
                    if m:
                        cur = int(m.group(1))
                        mx = int(m.group(2))
                        if mx > 0 and 0 <= cur <= mx:
                            hp = (cur / mx) * 100.0
                            if hp > best_hp_percent:
                                best_hp_percent = hp
                                best_method = f"ocr_region_{i}"
                except ImportError:
                    # Silent fallback to color-only
                    pass
                except Exception as e:
                    self.status_signal.emit(f"OCR failed on region {i}: {e}")

                # Heuristic color fallback only for meaningful signals
                if green_density >= 8:
                    hp_guess = 100.0
                elif green_density >= 4:
                    hp_guess = 75.0
                elif green_density >= 2:
                    hp_guess = 25.0
                else:
                    hp_guess = -1.0  # Treat as unknown rather than 0%

                if hp_guess > best_hp_percent:
                    best_hp_percent = hp_guess
                    best_method = f"color_region_{i}" if hp_guess >= 0 else best_method

            # Periodic debug
            self._debug_counter = getattr(self, '_debug_counter', 0) + 1
            if self._debug_counter % 60 == 0:
                self.status_signal.emit(
                    f"HP Best: {0 if best_hp_percent < 0 else best_hp_percent:.1f}% (Method: {best_method})"
                )

            # None indicates unknown/unreliable -> do NOT nexus on this
            return None if best_hp_percent < 0 else float(min(100.0, max(0.0, best_hp_percent)))

        except Exception as e:
            self.status_signal.emit(f"HP detection failed: {e}")
            return None

    def find_enemies(self, frame):
        """Detect enemies using simple color detection."""
        try:
            enemies = []
            h, w = frame.shape[:2]
            
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Look for enemy-like colors (red, orange, purple)
            # This is a simplified approach
            color_ranges = [
                (np.array([0, 100, 100]), np.array([10, 255, 255])),  # Red
                (np.array([10, 100, 100]), np.array([25, 255, 255])),  # Orange
                (np.array([130, 100, 100]), np.array([170, 255, 255])),  # Purple
            ]
            
            for lower, upper in color_ranges:
                mask = cv2.inRange(hsv, lower, upper)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    if cv2.contourArea(contour) > 100:  # Filter small noise
                        x, y, w_contour, h_contour = cv2.boundingRect(contour)
                        cx = x + w_contour // 2
                        cy = y + h_contour // 2
                        dist = math.hypot(cx - w // 2, cy - h // 2)
                        enemies.append({'center': (cx, cy), 'distance': dist, 'size': (w_contour, h_contour)})
            
            return enemies
            
        except Exception as e:
            self.status_signal.emit(f"Enemy detection failed: {e}")
            return []

    def find_bullets(self, frame):
        """Detect bullets/projectiles using color detection."""
        try:
            bullets = []
            h, w = frame.shape[:2]
            
            # Convert to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Look for bullet-like colors (white, yellow, cyan)
            color_ranges = [
                (np.array([0, 0, 200]), np.array([180, 30, 255])),  # White
                (np.array([20, 100, 100]), np.array([30, 255, 255])),  # Yellow
                (np.array([85, 100, 100]), np.array([95, 255, 255])),  # Cyan
            ]
            
            for lower, upper in color_ranges:
                mask = cv2.inRange(hsv, lower, upper)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if 10 < area < 500:  # Bullet-sized objects
                        x, y, w_contour, h_contour = cv2.boundingRect(contour)
                        cx = x + w_contour // 2
                        cy = y + h_contour // 2
                        bullets.append({'center': (cx, cy), 'size': (w_contour, h_contour)})
            
            return bullets
            
        except Exception as e:
            self.status_signal.emit(f"Bullet detection failed: {e}")
            return []

    def should_nexus(self, hp_percent):
        """Determine if the player should nexus based on HP.
        Requires multiple consecutive low-HP readings and ignores unknown HP.
        """
        if hp_percent is None:
            # Unknown reading: never nexus based on this frame
            self._low_hp_consecutive_count = 0
            return False

        if hp_percent <= self.auto_nexus_percent:
            self._low_hp_consecutive_count += 1
        else:
            self._low_hp_consecutive_count = 0

        # Require ~0.5s of consistent low HP at ~30 FPS (~15 frames)
        return self._low_hp_consecutive_count >= 15

    def get_dodge_direction(self, bullets, player_pos):
        """Calculate the best direction to dodge bullets."""
        if not bullets:
            return None
        
        # Simple dodge logic - move away from closest bullet
        closest_bullet = min(bullets, key=lambda b: math.hypot(
            b['center'][0] - player_pos[0], 
            b['center'][1] - player_pos[1]
        ))
        
        dx = player_pos[0] - closest_bullet['center'][0]
        dy = player_pos[1] - closest_bullet['center'][1]
        
        # Normalize and return direction
        length = math.hypot(dx, dy)
        if length > 0:
            return (dx / length, dy / length)
        return None

    def move_towards(self, direction):
        """Move the character in the specified direction."""
        if not direction:
            return
        
        dx, dy = direction
        
        # Determine primary movement direction
        if abs(dx) > abs(dy):
            # Horizontal movement
            if dx > 0:
                keyboard.press_key(self.keybinds.get('move_right', 'd'))
                keyboard.release_key(self.keybinds.get('move_left', 'a'))
            else:
                keyboard.press_key(self.keybinds.get('move_left', 'a'))
                keyboard.release_key(self.keybinds.get('move_right', 'd'))
        else:
            # Vertical movement
            if dy > 0:
                keyboard.press_key(self.keybinds.get('move_down', 's'))
                keyboard.release_key(self.keybinds.get('move_up', 'w'))
            else:
                keyboard.press_key(self.keybinds.get('move_up', 'w'))
                keyboard.release_key(self.keybinds.get('move_down', 's'))

    def stop_movement(self):
        """Stop all movement."""
        for key in ['move_up', 'move_down', 'move_left', 'move_right']:
            keyboard.release_key(self.keybinds.get(key, 'wasd'[key.index('move_')]))

    def attack(self):
        """Perform attack action."""
        attack_key = self.keybinds.get('attack', 'left')
        if attack_key == 'left':
            mouse.click('left')
        else:
            keyboard.tap_key(attack_key)

    def nexus(self):
        """Perform nexus action."""
        nexus_key = self.keybinds.get('nexus', 'r')
        keyboard.tap_key(nexus_key)
        self.status_signal.emit("NEXUSING!")

    def run(self):
        """Main bot loop. Runs at ~30 FPS performing vision and actions."""
        logging.info("Bot loop started.")
        self.status_signal.emit("Bot started - beginning main loop...")
        self._running = True

        loop_count = 0
        last_attack_time = 0
        
        try:
            while self._running:
                loop_start = time.time()
                loop_count += 1
                
                # Log every 30 loops (about once per second)
                if loop_count % 30 == 0:
                    self.status_signal.emit(f"Bot running - loop {loop_count}")
                
                try:
                    # 1. Screen capture (now targets RotMG window specifically)
                    frame = self.capture_screen()
                    if frame is None:
                        self.status_signal.emit("Screen capture returned None, skipping frame")
                        time.sleep(0.5)  # Add delay to prevent rapid error loops
                        continue

                    # 2. Vision: detect game elements
                    player_hp = self.get_hp_percent(frame)
                    enemies = self.find_enemies(frame)
                    bullets = self.find_bullets(frame)
                    
                    # 3. Decision making
                    
                    # Check if should nexus
                    if self.should_nexus(player_hp):
                        self.nexus()
                        time.sleep(1)  # Wait for nexus
                        continue
                    
                    # Get player position (center of screen)
                    h, w = frame.shape[:2]
                    player_pos = (w // 2, h // 2)
                    
                    # Movement logic
                    if self.movement_mode.lower() == 'kiting':
                        # Kiting: move away from enemies while attacking
                        if enemies:
                            closest_enemy = min(enemies, key=lambda e: e['distance'])
                            if closest_enemy['distance'] < 200:  # Too close
                                dodge_dir = self.get_dodge_direction(bullets, player_pos)
                                if dodge_dir:
                                    self.move_towards(dodge_dir)
                                else:
                                    # Move away from closest enemy
                                    dx = player_pos[0] - closest_enemy['center'][0]
                                    dy = player_pos[1] - closest_enemy['center'][1]
                                    length = math.hypot(dx, dy)
                                    if length > 0:
                                        self.move_towards((dx / length, dy / length))
                            else:
                                self.stop_movement()
                        else:
                            self.stop_movement()
                    
                    elif self.movement_mode.lower() == 'circle-strafe':
                        # Circle-strafe: move in circles around enemies
                        if enemies:
                            # Simple circle movement
                            angle = (loop_count * 10) % 360
                            rad = math.radians(angle)
                            dx = math.cos(rad)
                            dy = math.sin(rad)
                            self.move_towards((dx, dy))
                        else:
                            self.stop_movement()
                    
                    # Attack logic
                    current_time = time.time()
                    if current_time - last_attack_time > 0.1:  # Attack every 100ms
                        if enemies:
                            self.attack()
                            last_attack_time = current_time
                    
                    # Log detection results occasionally
                    if loop_count % 60 == 0:  # Every 2 seconds
                        self.status_signal.emit(f"HP: {player_hp:.1f}%, Enemies: {len(enemies)}, Bullets: {len(bullets)}")
                        
                except Exception as e:
                    self.status_signal.emit(f"Bot loop error: {e}")
                    logging.error(f"Bot loop error: {e}")
                    import traceback
                    logging.error(f"Traceback: {traceback.format_exc()}")
                    time.sleep(0.1)
                    continue
                
                # Maintain ~30 FPS
                elapsed = time.time() - loop_start
                if elapsed < 0.033:  # 30 FPS = 33ms per frame
                    time.sleep(0.033 - elapsed)
            
        except Exception as e:
            logging.error(f"Critical bot error: {e}")
            import traceback
            logging.error(f"Critical traceback: {traceback.format_exc()}")
            self.status_signal.emit(f"Critical bot error: {e}")
        
        # Cleanup
        self.stop_movement()
        self.status_signal.emit("Bot stopped.")
        logging.info("Bot loop ended.")
