import time
import math
import logging
from PySide6.QtCore import QObject, Signal

from vision import detection
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
        self.keybinds = config.get('keybinds', {})  # e.g. {'move_up':'w', 'attack':'left_mouse', ...}
        # Internal state
        self._running = False
        self.inventory_full = False  # track if inventory full (for looting logic)
        # Initialize input controllers and state trackers
        self.keyboard = keyboard.Controller()      # for sending keystrokes
        self.mouse = mouse.Controller()            # for sending mouse moves/clicks
        self.user_input_monitor = keyboard.Listener(on_press=self.on_user_key)  # detect user key presses
        self.user_input_monitor.start()
        # Determine game window focus if needed (not explicitly used here, but can be integrated)
        logging.info("Bot initialized with auto_nexus_percent=%d, movement_mode=%s" % 
                     (self.auto_nexus_percent, self.movement_mode))

    def on_user_key(self, key):
        """Callback for user key press events. If user presses movement keys, pause bot."""
        try:
            k = key.char.lower()
        except AttributeError:
            # special keys (e.g., Key.shift) have no char
            k = str(key)
        # Only pause if user presses a special key combination (e.g., Ctrl+Q to stop)
        # For now, let's disable automatic pausing on WASD to allow the bot to work
        if hasattr(key, 'ctrl') and key.ctrl and k == 'q':
            logging.info("User pressed Ctrl+Q, stopping bot.")
            self.status_signal.emit("User pressed Ctrl+Q, stopping bot.")
            self._running = False

    def stop(self):
        """Signal the bot loop to stop gracefully."""
        self._running = False

    def run(self):
        """Main bot loop. Runs at ~60 FPS performing vision and actions."""
        logging.info("Bot loop started.")
        self.status_signal.emit("Bot started - beginning main loop...")
        self._running = True

        # Use the selected player class from config
        self.status_signal.emit("Capturing initial screen...")
        frame = detection.capture_screen()  # capture one frame
        self.status_signal.emit("Screen captured successfully")
        
        logging.info(f"Using player class: {self.player_class}")
        self.status_signal.emit(f"Player class set to: {self.player_class}")

        # Main loop
        prev_time = time.time()
        loop_count = 0
        while self._running:
            loop_start = time.time()
            loop_count += 1
            
            # Log every 60 loops (about once per second)
            if loop_count % 60 == 0:
                self.status_signal.emit(f"Bot running - loop {loop_count}")
            
            # 1. Screen capture
            try:
                frame = detection.capture_screen()
            except Exception as e:
                self.status_signal.emit(f"Screen capture failed: {e}")
                time.sleep(0.1)
                continue

            # 2. Vision: detect game elements
            try:
                player_hp = detection.get_hp_percent(frame)
                enemies = detection.find_enemies(frame)
                bullets = detection.find_bullets(frame)
                loot_items = detection.find_loot(frame)
                obstacles = detection.find_obstacles(frame)  # e.g., walls/rocks on screen
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
            # Auto-Nexus: if HP below threshold, trigger Nexus (escape to safety)
            if player_hp is not None and player_hp <= self.auto_nexus_percent:
                logging.warning(f"HP {player_hp}% <= threshold! Auto-Nexus activated.")
                self.status_signal.emit("Auto-Nexus triggered! HP low.")
                # Press the Nexus key (teleport to Nexus). RotMG default is usually 'R' or similar.
                nexus_key = self.keybinds.get('nexus', 'r')
                self.keyboard.tap_key(nexus_key)
                time.sleep(1)  # small delay after nexusing
                self._running = False
                continue  # break out of loop after nexusing (bot will stop)

            # If an enemy is detected:
            if enemies:
                target = enemies[0]  # take first enemy (or could select nearest or priority target)
                ex, ey = target['center']  # target coordinates on screen
                # Aim at enemy: move mouse to enemy position
                self.mouse.move_to(ex, ey)
                # Attack: if not already firing, press attack key or mouse
                # (In RotMG, continuous shooting might be toggle or hold; assuming left mouse hold to shoot)
                self.mouse.click(button='left')  # simulate a quick shot; for continuous fire, handle differently
                self.status_signal.emit(f"Enemy detected at {target['center']}, attacking.")
                logging.info(f"Aiming and attacking enemy at {target['center']}.")
                # Movement: approach or maintain distance based on mode
                if self.movement_mode.lower().startswith("kit"):  # Kiting
                    # Kiting: maintain distance from target. Move away if too close.
                    if target['distance'] < 100:  # if enemy too close (100 px as example)
                        # Move opposite to enemy direction
                        dx = target['center'][0] - frame.shape[1]//2
                        dy = target['center'][1] - frame.shape[0]//2
                        # Invert direction to move away
                        move_x = -dx; move_y = -dy
                        keyboard.move_towards(move_x, move_y, self.keyboard, self.keybinds)
                    else:
                        # If at a safe distance, maybe strafe a bit or stand still
                        keyboard.release_movement_keys(self.keyboard, self.keybinds)
                else:
                    # Circle-Strafe: move perpendicular to enemy (circle around)
                    dx = target['center'][0] - frame.shape[1]//2
                    dy = target['center'][1] - frame.shape[0]//2
                    # Determine perpendicular direction vector (swap dx,dy and invert one)
                    perp_x, perp_y = -dy, dx
                    keyboard.move_towards(perp_x, perp_y, self.keyboard, self.keybinds)
            else:
                # No enemies seen, stop moving/attacking
                keyboard.release_movement_keys(self.keyboard, self.keybinds)
            
            # If bullets (enemy projectiles) detected, perform dodge maneuver
            if bullets:
                for b in bullets:
                    bx, by = b['center']
                    # If a bullet is within some danger radius of player (e.g., 50px and incoming)
                    if detection.is_bullet_dangerous(b):
                        # Dodge: move perpendicular to bullet trajectory quickly
                        dodge_dir = detection.get_dodge_direction(b)
                        keyboard.move_direction(dodge_dir, self.keyboard, self.keybinds, duration=0.1)
                        self.status_signal.emit("Dodging projectile!")
                        logging.info(f"Dodging bullet at {b['center']}.")

            # Looting logic: if any loot on ground and conditions met
            if loot_items:
                # If inventory full, drop worst item first (to free space)
                if self.inventory_full:
                    worst_slot = detection.find_worst_item_slot(frame)
                    if worst_slot is not None:
                        # Simulate dropping the item from that slot (e.g., press key to drop or drag out)
                        logging.info(f"Inventory full. Dropping item in slot {worst_slot}.")
                        self.status_signal.emit("Inventory full; dropping least valuable item.")
                        mouse.drop_item(worst_slot, self.mouse, self.keybinds)
                        time.sleep(0.5)  # short delay for drop action
                        self.inventory_full = False  # assume one slot freed
                # Now pick up desired loot
                for item in loot_items:
                    item_name = item['name']
                    value = detection.get_item_value(item_name)
                    if value and value >= 0:  # assume -1 or None for items we don't want
                        # Move to loot position and pick it up
                        ix, iy = item['center']
                        self.mouse.move_to(ix, iy)
                        self.mouse.click(button='left')  # click the loot bag or item
                        logging.info(f"Picking up loot: {item_name} at {item['center']}")
                        self.status_signal.emit(f"Looting item: {item_name}")
                        time.sleep(0.2)  # small delay for pickup
                        break  # pick one item at a time
            # End of decision-making

            # 4. Maintain loop timing ~60 FPS
            loop_end = time.time()
            elapsed = loop_end - loop_start
            # Sleep to keep frame rate (if processing was fast)
            if elapsed < 1/60:
                time.sleep(1/60 - elapsed)

        logging.info("Bot loop terminated.")
        self.status_signal.emit("Bot stopped.")
        # Ensure movement keys released when stopping
        keyboard.release_movement_keys(self.keyboard, self.keybinds)
        # Stop listening to user input to avoid thread leak
        self.user_input_monitor.stop()
