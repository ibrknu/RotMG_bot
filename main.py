#!/usr/bin/env python3
import sys
import logging
import os

# Configure Qt environment before importing any Qt modules
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''
os.environ['QT_DEBUG_PLUGINS'] = '0'  # Disable debug output
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.*=false'  # Disable Qt platform warnings

# Importing our modules
from PySide6.QtWidgets import QApplication
from gui.window import BotWindow
from config import settings
config = settings.load_config()

# Configure logging to file in logs/ folder
logging.basicConfig(
    filename='logs/bot.log', 
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logging.info("Bot starting up...")

# Load settings (or create default config if none exists)
config = settings.load_config()  # returns a dict of settings

if __name__ == "__main__":
    # Create Qt application and main window
    app = QApplication(sys.argv)
    window = BotWindow(config)
    window.show()
    logging.info("GUI initialized, launching application event loop.")
    sys.exit(app.exec())
