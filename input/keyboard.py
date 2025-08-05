
from pynput import keyboard as pynput_keyboard

# Create a global keyboard Controller for sending keys
_keyboard_controller = pynput_keyboard.Controller()

# We can also use Xlib for lower-level control if needed. Here, we rely on pynput for simplicity.

def Controller():
    """Returns a keyboard controller object for sending key presses."""
    return _keyboard_controller

def Listener(on_press=None, on_release=None):
    """Returns a keyboard listener to detect user key events globally."""
    return pynput_keyboard.Listener(on_press=on_press, on_release=on_release)

def tap_key(key):
    """Tap (press and release) a given key."""
    _keyboard_controller.press(key)
    _keyboard_controller.release(key)

def press_key(key):
    """Press and hold a given key."""
    _keyboard_controller.press(key)

def release_key(key):
    """Release a given key."""
    _keyboard_controller.release(key)

def move_towards(dx, dy, controller, keybinds):
    """Press movement keys to move in the direction of vector (dx, dy). Uses WASD keys from keybinds."""
    # Determine primary direction
    # If magnitude in x is greater than y, move horizontal, else vertical (this simplifies diagonal handling)
    try:
        left_key = keybinds.get('move_left', 'a')
        right_key = keybinds.get('move_right', 'd')
        up_key = keybinds.get('move_up', 'w')
        down_key = keybinds.get('move_down', 's')
    except AttributeError:
        # keybinds might not be a dict
        left_key, right_key, up_key, down_key = 'a', 'd', 'w', 's'

    if abs(dx) > abs(dy):
        # horizontal movement
        if dx < 0:
            controller.press(left_key)
            controller.release(right_key)
        else:
            controller.press(right_key)
            controller.release(left_key)
        # minimal vertical
        controller.release(up_key)
        controller.release(down_key)
    else:
        # vertical movement
        if dy < 0:
            controller.press(up_key)
            controller.release(down_key)
        else:
            controller.press(down_key)
            controller.release(up_key)
        # minimal horizontal
        controller.release(left_key)
        controller.release(right_key)

def move_direction(direction, controller, keybinds, duration=0.1):
    """Tap movement in a cardinal direction ('up','down','left','right') for a short duration."""
    key_map = {
        'up': keybinds.get('move_up', 'w'),
        'down': keybinds.get('move_down', 's'),
        'left': keybinds.get('move_left', 'a'),
        'right': keybinds.get('move_right', 'd')
    }
    key = key_map.get(direction)
    if not key:
        return
    controller.press(key)
    # Hold for the specified duration (in seconds) then release
    import time
    time.sleep(duration)
    controller.release(key)

def release_movement_keys(controller, keybinds):
    """Release all movement keys (WASD) to stop movement."""
    for action, key in keybinds.items():
        if action.startswith('move_'):
            try:
                controller.release(key)
            except Exception:
                continue
