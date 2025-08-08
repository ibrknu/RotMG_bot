from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PySide6.QtWidgets import QLabel, QSlider, QComboBox, QGroupBox, QFormLayout, QLineEdit, QTextEdit
from PySide6.QtCore import Qt, QThread, Signal
import logging

# Import will be handled dynamically based on bot_class parameter

class BotWindow(QMainWindow):
    """Main application window with controls for the RotMG bot."""
    # Define custom signal to update status text from bot thread
    status_updated = Signal(str)

    def __init__(self, config, bot_class=None):
        super().__init__()
        self.setWindowTitle("RotMG Bot Control - Linux")
        self.resize(400, 300)  # initial size, but can be resized
        
        # Use specified bot class or default to Windows version
        self.bot_class = bot_class

        # Central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Start/Stop button
        self.start_button = QPushButton("Start Bot")
        self.start_button.setCheckable(True)  # toggle button
        layout.addWidget(self.start_button)

        # Auto-Nexus HP threshold slider
        thresh_layout = QHBoxLayout()
        thresh_label = QLabel("Auto-Nexus HP%:")
        self.thresh_slider = QSlider(Qt.Horizontal)
        self.thresh_slider.setRange(0, 100)
        self.thresh_slider.setValue(config.get("auto_nexus_percent", 30))  # default 30%
        self.thresh_percent_label = QLabel(f"{self.thresh_slider.value()}%")
        thresh_layout.addWidget(thresh_label)
        thresh_layout.addWidget(self.thresh_slider)
        thresh_layout.addWidget(self.thresh_percent_label)
        layout.addLayout(thresh_layout)

        # Movement behavior selection (kiting or circle-strafe)
        move_layout = QHBoxLayout()
        move_label = QLabel("Movement Mode:")
        self.move_combo = QComboBox()
        self.move_combo.addItems(["Kiting", "Circle-Strafe"])
        # Set initial selection from config
        default_mode = config.get("movement_mode", "Kiting")
        index = 0 if default_mode.lower().startswith("kit") else 1
        self.move_combo.setCurrentIndex(index)
        move_layout.addWidget(move_label)
        move_layout.addWidget(self.move_combo)
        layout.addLayout(move_layout)

        # Player class selection
        class_layout = QHBoxLayout()
        class_label = QLabel("Player Class:")
        self.class_combo = QComboBox()
        self.class_combo.addItems([
            "Wizard", "Archer", "Huntress", "Warrior", "Knight", "Paladin",
            "Priest", "Mystic", "Necromancer", "Sorcerer", "Rogue", "Assassin",
            "Trickster", "Ninja", "Samurai", "Bard", "Summoner", "Kensei"
        ])
        # Set initial selection from config
        default_class = config.get("player_class", "Wizard")
        class_index = self.class_combo.findText(default_class)
        if class_index >= 0:
            self.class_combo.setCurrentIndex(class_index)
        class_layout.addWidget(class_label)
        class_layout.addWidget(self.class_combo)
        layout.addLayout(class_layout)

        # Keybindings remap UI (simplified as text inputs for each key)
        kb_group = QGroupBox("Key Bindings")
        kb_form = QFormLayout()
        # We assume config has default keys for actions
        self.key_inputs = {}
        for action, default_key in config.get("keybinds", {}).items():
            line_edit = QLineEdit(default_key)
            kb_form.addRow(f"{action}:", line_edit)
            self.key_inputs[action] = line_edit
        kb_group.setLayout(kb_form)
        layout.addWidget(kb_group)

        # Status output (multiline text area for live updates)
        self.status_area = QTextEdit()
        self.status_area.setReadOnly(True)
        self.status_area.setPlaceholderText("Status messages will appear here...")
        layout.addWidget(self.status_area)

        # Add window detection status
        window_status_layout = QHBoxLayout()
        self.window_status_label = QLabel("RotMG Window: Not Detected")
        self.window_status_label.setStyleSheet("color: red; font-weight: bold;")
        self.refresh_window_button = QPushButton("Refresh Window Detection")
        self.refresh_window_button.clicked.connect(self.refresh_window_detection)
        window_status_layout.addWidget(self.window_status_label)
        window_status_layout.addWidget(self.refresh_window_button)
        layout.addLayout(window_status_layout)

        # Connect signals to slots
        self.start_button.clicked.connect(self.toggle_bot)
        self.thresh_slider.valueChanged.connect(self.update_threshold)
        self.move_combo.currentIndexChanged.connect(self.update_movement_mode)
        self.class_combo.currentIndexChanged.connect(self.update_player_class)
        self.status_updated.connect(self.append_status)  # custom signal to update text

        # Bot thread is initially not running
        self.bot_thread = None
        self.bot = None  # will hold bot instance

        # Save reference to config for future use
        self.config = config
        
        # Add initial status message
        self.append_status("Bot GUI loaded successfully. Click 'Start Bot' to begin.")
        self.append_status("Press Ctrl+Q to stop the bot while it's running.")

    def toggle_bot(self):
        """Start or stop the bot based on button state."""
        if self.start_button.isChecked():
            self.start_bot()
        else:
            self.stop_bot()

    def refresh_window_detection(self):
        """Refresh the RotMG window detection."""
        try:
            self.append_status("Refreshing window detection...")
            
            if self.bot:
                self.bot.find_rotmg_window()
                if self.bot.rotmg_window_handle:
                    self.window_status_label.setText("RotMG Window: Detected")
                    self.window_status_label.setStyleSheet("color: green; font-weight: bold;")
                    self.append_status("RotMG window detected successfully!")
                else:
                    self.window_status_label.setText("RotMG Window: Not Found")
                    self.window_status_label.setStyleSheet("color: red; font-weight: bold;")
                    self.append_status("RotMG window not found. Make sure the game is running.")
            else:
                # Create a temporary bot instance to test window detection
                from logic.bot import RotMGbot
                temp_bot = RotMGbot(self.config)
                if temp_bot.rotmg_window_handle:
                    self.window_status_label.setText("RotMG Window: Detected")
                    self.window_status_label.setStyleSheet("color: green; font-weight: bold;")
                    self.append_status("RotMG window detected successfully!")
                else:
                    self.window_status_label.setText("RotMG Window: Not Found")
                    self.window_status_label.setStyleSheet("color: red; font-weight: bold;")
                    self.append_status("RotMG window not found. Make sure the game is running.")
                    
        except Exception as e:
            self.append_status(f"Error refreshing window detection: {e}")

    def start_bot(self):
        """Start the bot in a separate thread."""
        try:
            self.append_status("Starting bot...")
            self.start_button.setText("Stop Bot")
            
            # Update config with current settings
            self.update_config_from_ui()
            
            # Create bot instance with specified class or default
            if self.bot_class:
                self.bot = self.bot_class(config=self.config)
            else:
                from logic.bot import RotMGbot
                self.bot = RotMGbot(config=self.config)
            
            # Update window status
            if self.bot.rotmg_window_handle:
                self.window_status_label.setText("RotMG Window: Detected")
                self.window_status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.window_status_label.setText("RotMG Window: Not Found")
                self.window_status_label.setStyleSheet("color: red; font-weight: bold;")
            
            # Connect bot signals to UI
            if hasattr(self.bot, 'status_signal'):
                self.bot.status_signal.connect(self.status_updated)
            
            # Create and start thread
            self.bot_thread = QThread()
            self.bot.moveToThread(self.bot_thread)
            self.bot_thread.started.connect(self.bot.run)
            
            # Clean up thread on finish
            self.bot_thread.finished.connect(self.bot_thread.deleteLater)
            self.bot_thread.finished.connect(self.on_bot_finished)
            
            # Note: errorOccurred is not available in all PySide6 versions
            # self.bot_thread.errorOccurred.connect(self.on_thread_error)
            
            # Start the thread
            self.bot_thread.start()
            
            self.append_status("Bot started successfully!")
            self.append_status("Bot is now running and will control your character.")
            self.append_status("Make sure RotMG is in focus and visible on screen.")
            
        except Exception as e:
            self.append_status(f"Error starting bot: {e}")
            logging.error(f"Failed to start bot: {e}")
            import traceback
            logging.error(f"Start bot traceback: {traceback.format_exc()}")
            self.start_button.setChecked(False)

    def stop_bot(self):
        """Stop the bot."""
        try:
            self.append_status("Stopping bot...")
            self.start_button.setText("Start Bot")
            
            # Force stop the bot
            if self.bot:
                self.bot.stop()
                self.bot._running = False  # Force stop
            
            # Force quit the thread
            if self.bot_thread and self.bot_thread.isRunning():
                self.bot_thread.quit()
                if not self.bot_thread.wait(3000):  # Wait up to 3 seconds
                    self.bot_thread.terminate()  # Force terminate if needed
                    self.bot_thread.wait()
            
            self.bot = None
            self.bot_thread = None
            
            self.append_status("Bot stopped.")
            
        except Exception as e:
            self.append_status(f"Error stopping bot: {e}")
            logging.error(f"Failed to stop bot: {e}")
            # Force cleanup
            self.bot = None
            self.bot_thread = None
            self.start_button.setChecked(False)
            self.start_button.setText("Start Bot")

    def on_thread_error(self, error):
        """Handle thread errors."""
        self.append_status(f"Thread error: {error}")
        logging.error(f"Thread error: {error}")

    def on_bot_finished(self):
        """Called when the bot thread finishes."""
        self.start_button.setChecked(False)
        self.start_button.setText("Start Bot")
        self.append_status("Bot thread finished.")
        logging.info("Bot thread finished")

    def update_config_from_ui(self):
        """Update the config with current UI values."""
        self.config['auto_nexus_percent'] = self.thresh_slider.value()
        self.config['movement_mode'] = self.move_combo.currentText()
        self.config['player_class'] = self.class_combo.currentText()
        
        # Update keybinds
        for action, line_edit in self.key_inputs.items():
            self.config['keybinds'][action] = line_edit.text()

    def update_threshold(self, value):
        """Update the auto-nexus threshold percentage."""
        self.thresh_percent_label.setText(f"{value}%")
        self.config['auto_nexus_percent'] = value
        if self.bot:
            self.bot.auto_nexus_percent = value
        self.append_status(f"Auto-nexus threshold set to {value}%")

    def update_movement_mode(self, index):
        """Update the movement mode selection."""
        mode = self.move_combo.currentText()
        self.config['movement_mode'] = mode
        if self.bot:
            self.bot.movement_mode = mode
        self.append_status(f"Movement mode set to: {mode}")

    def update_player_class(self, index):
        """Update the player class selection."""
        player_class = self.class_combo.currentText()
        self.config['player_class'] = player_class
        if self.bot:
            self.bot.player_class = player_class
        self.append_status(f"Player class set to: {player_class}")

    def append_status(self, text):
        """Add a status message to the text area."""
        self.status_area.append(text)
        # Auto-scroll to bottom
        self.status_area.verticalScrollBar().setValue(
            self.status_area.verticalScrollBar().maximum()
        )
