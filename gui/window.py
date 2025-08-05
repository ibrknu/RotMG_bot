from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PySide6.QtWidgets import QLabel, QSlider, QComboBox, QGroupBox, QFormLayout, QLineEdit, QTextEdit
from PySide6.QtCore import Qt, QThread, Signal

from logic.bot import RotMGbot

class BotWindow(QMainWindow):
    """Main application window with controls for the RotMG bot."""
    # Define custom signal to update status text from bot thread
    status_updated = Signal(str)

    def __init__(self, config):
        super().__init__()
        self.setWindowTitle("RotMG Bot Control")
        self.resize(400, 300)  # initial size, but can be resized

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

        # Connect signals to slots
        self.start_button.clicked.connect(self.toggle_bot)
        self.thresh_slider.valueChanged.connect(self.update_threshold)
        self.move_combo.currentIndexChanged.connect(self.update_movement_mode)
        self.class_combo.currentIndexChanged.connect(self.update_player_class)
        self.status_updated.connect(self.append_status)  # custom signal to update text

        # Bot thread is initially not running
        self.bot_thread = None
        self.bot = None  # will hold RotMGbot instance

        # Save reference to config for future use
        self.config = config

    def toggle_bot(self):
        """Start or stop the bot when the button is toggled."""
        if self.start_button.isChecked():
            # Start the bot
            self.start_button.setText("Stop Bot")
            # Create bot instance and thread
            self.bot = RotMGbot(config=self.config)
            # Connect bot signals to UI (if any signals exist)
            if hasattr(self.bot, 'status_signal'):
                self.bot.status_signal.connect(self.status_updated)  # bot will emit status text
            # Start in a QThread for continuous loop
            self.bot_thread = QThread()
            self.bot.moveToThread(self.bot_thread)
            self.bot_thread.started.connect(self.bot.run)  # call run method on thread start
            # Clean up thread on finish
            self.bot_thread.finished.connect(self.bot_thread.deleteLater)
            self.bot_thread.start()
        else:
            # Stop the bot
            self.start_button.setText("Start Bot")
            if self.bot:
                self.bot.stop()           # signal the bot loop to stop
            if self.bot_thread:
                self.bot_thread.quit()
                self.bot_thread.wait()
            self.bot = None

    def update_threshold(self, value):
        """Update the auto-Nexus HP threshold in config when slider is moved."""
        self.config['auto_nexus_percent'] = value
        self.thresh_percent_label.setText(f"{value}%")
        if self.bot:
            self.bot.auto_nexus_percent = value

    def update_movement_mode(self, index):
        """Update movement behavior mode in config."""
        mode = "Kiting" if index == 0 else "Circle-Strafe"
        self.config['movement_mode'] = mode
        if self.bot:
            self.bot.movement_mode = mode

    def update_player_class(self, index):
        """Update player class in config."""
        player_class = self.class_combo.currentText()
        self.config['player_class'] = player_class
        if self.bot:
            self.bot.player_class = player_class

    def append_status(self, text):
        """Append a new status message to the status text area."""
        self.status_area.append(text)
        # Auto-scroll to bottom
        self.status_area.verticalScrollBar().setValue(self.status_area.verticalScrollBar().maximum())
