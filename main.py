#!/usr/bin/env python3
import sys
import logging
import os
import traceback

# Configure Qt environment before importing any Qt modules
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''
os.environ['QT_DEBUG_PLUGINS'] = '0'  # Disable debug output
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.*=false'  # Disable Qt platform warnings

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging to file in logs/ folder
logging.basicConfig(
    filename='logs/bot.log', 
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

try:
    # Importing our modules
    from PySide6.QtWidgets import QApplication
    from gui.window import BotWindow
    from config import settings
    
    logging.info("Bot starting up...")
    
    # Load settings (or create default config if none exists)
    config = settings.load_config()  # returns a dict of settings
    
    if __name__ == "__main__":
        # Create Qt application and main window
        app = QApplication(sys.argv)
        
        try:
            window = BotWindow(config)
            window.show()
            logging.info("GUI initialized, launching application event loop.")
            sys.exit(app.exec())
        except Exception as e:
            logging.error(f"Failed to create GUI: {e}")
            logging.error(traceback.format_exc())
            print(f"Error creating GUI: {e}")
            sys.exit(1)
            
except ImportError as e:
    logging.error(f"Import error: {e}")
    print(f"Import error: {e}")
    print("Please install required dependencies: pip install PySide6 mss numpy opencv-python pynput")
    sys.exit(1)
except Exception as e:
    logging.error(f"Unexpected error: {e}")
    logging.error(traceback.format_exc())
    print(f"Unexpected error: {e}")
    sys.exit(1)
