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
from logic.bot_linux import RotMGbotLinux

# Configure logging to file in logs/ folder
logging.basicConfig(
    filename='logs/bot_linux.log', 
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logging.info("Linux RotMG Bot starting up...")

# Load settings (or create default config if none exists)
config = settings.load_config()

if __name__ == "__main__":
    # Create Qt application and main window
    app = QApplication(sys.argv)
    
    # Create window with Linux bot
    window = BotWindow(config, bot_class=RotMGbotLinux)
    window.show()
    
    logging.info("Linux GUI initialized, launching application event loop.")
    sys.exit(app.exec()) 