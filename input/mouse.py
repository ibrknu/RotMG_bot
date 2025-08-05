from pynput import mouse as pynput_mouse

_mouse_controller = pynput_mouse.Controller()

def Controller():
    """Returns a mouse controller for moving and clicking."""
    return _mouse_controller

def move_to(x, y):
    """Move mouse cursor to (x, y) on screen."""
    try:
        _mouse_controller.position = (x, y)
    except Exception as e:
        print(f"Mouse move failed: {e}")

def click(button='left'):
    """Click the specified mouse button once."""
    btn = pynput_mouse.Button.left if button == 'left' else pynput_mouse.Button.right
    _mouse_controller.press(btn)
    _mouse_controller.release(btn)

def drop_item(slot_index, controller, keybinds):
    """Simulate dropping an item from the given inventory slot index."""
    # This could move the mouse to the inventory slot and right-click or drag out of inventory.
    # For simplicity, we'll assume pressing a key to drop (if game had a hotkey), or do nothing.
    # (Implementing actual drag-and-drop would require knowing slot coordinates and using move_to & click).
    drop_key = keybinds.get('drop_item', None)
    if drop_key:
        # If a drop key is defined (for example, some games use Del key to drop items)
        from input import keyboard
        keyboard.tap_key(drop_key)
    else:
        # If not, we could try to drag the item out:
        # Calculate slot coordinates if we know inventory layout (not implemented in this example).
        pass
