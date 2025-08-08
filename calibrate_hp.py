#!/usr/bin/env python3
"""
HP Bar Calibration Tool
Helps users find the correct coordinates for their HP bar
"""
import cv2
import numpy as np
import mss
import json
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QSpinBox, QGroupBox, QFileDialog, QMessageBox, QApplication)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage

# Make pytesseract optional and handle missing binary gracefully
try:
    from pytesseract import TesseractNotFoundError as _TessErr
except Exception:  # pylint: disable=broad-except
    class _TessErr(Exception):
        pass

class HPCalibrator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HP Bar Calibrator")
        self.setGeometry(100, 100, 1000, 800)
        
        # Setup UI
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Screenshot display
        self.screenshot_label = QLabel("Screenshot will appear here")
        self.screenshot_label.setAlignment(Qt.AlignCenter)
        self.screenshot_label.setMinimumSize(800, 600)
        self.screenshot_label.setStyleSheet("border: 2px solid gray;")
        layout.addWidget(self.screenshot_label)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # HP Bar Region Controls
        hp_group = QGroupBox("HP Bar Region")
        hp_layout = QVBoxLayout()
        
        # X coordinate
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X:"))
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 3840)  # Support up to 4K
        self.x_spin.setValue(1150)  # Default based on screenshot
        x_layout.addWidget(self.x_spin)
        hp_layout.addLayout(x_layout)
        
        # Y coordinate
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y:"))
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 2160)  # Support up to 4K
        self.y_spin.setValue(350)  # Default based on screenshot
        y_layout.addWidget(self.y_spin)
        hp_layout.addLayout(y_layout)
        
        # Width
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Width:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 500)
        self.width_spin.setValue(100)  # Default based on screenshot
        width_layout.addWidget(self.width_spin)
        hp_layout.addLayout(width_layout)
        
        # Height
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Height:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 100)
        self.height_spin.setValue(20)  # Default based on screenshot
        height_layout.addWidget(self.height_spin)
        hp_layout.addLayout(height_layout)
        
        # Live update of overlay when values change
        self.x_spin.valueChanged.connect(self.update_display)
        self.y_spin.valueChanged.connect(self.update_display)
        self.width_spin.valueChanged.connect(self.update_display)
        self.height_spin.valueChanged.connect(self.update_display)

        hp_group.setLayout(hp_layout)
        controls_layout.addWidget(hp_group)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        self.load_btn = QPushButton("Load Screenshot")
        self.load_btn.clicked.connect(self.load_screenshot)
        button_layout.addWidget(self.load_btn)
        
        self.capture_btn = QPushButton("Capture Screenshot")
        self.capture_btn.clicked.connect(self.capture_screenshot)
        button_layout.addWidget(self.capture_btn)
        
        self.auto_detect_btn = QPushButton("Auto-Detect HP Bar")
        self.auto_detect_btn.clicked.connect(self.auto_detect_hp_bar)
        button_layout.addWidget(self.auto_detect_btn)
        
        self.save_btn = QPushButton("Save Configuration")
        self.save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_btn)
        
        self.test_btn = QPushButton("Test HP Detection")
        self.test_btn.clicked.connect(self.test_hp_detection)
        button_layout.addWidget(self.test_btn)
        
        controls_layout.addLayout(button_layout)
        layout.addLayout(controls_layout)
        
        # Status
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Current screenshot
        self.current_screenshot = None
        
        # Load existing config if available
        self.load_existing_config()
    
    def load_existing_config(self):
        """Load existing HP bar configuration if available"""
        try:
            config_path = "config/user_config.json"
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    hp_config = config.get('hp_bar_region', {})
                    self.x_spin.setValue(hp_config.get('x', self.x_spin.value()))
                    self.y_spin.setValue(hp_config.get('y', self.y_spin.value()))
                    self.width_spin.setValue(hp_config.get('width', self.width_spin.value()))
                    self.height_spin.setValue(hp_config.get('height', self.height_spin.value()))
        except Exception as e:
            self.status_label.setText(f"Failed to load config: {e}")
    
    def load_screenshot(self):
        """Load a screenshot from file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Screenshot", "", 
                "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
            )
            if file_path:
                frame = cv2.imread(file_path)
                if frame is not None:
                    self.current_screenshot = frame
                    self.update_display()
                    self.status_label.setText("Screenshot loaded")
                    # Auto-detect after loading
                    self.auto_detect_hp_bar()
                else:
                    self.status_label.setText("Failed to load image")
        except Exception as e:
            self.status_label.setText(f"Error loading screenshot: {e}")
    
    def capture_screenshot(self):
        """Capture a screenshot of the primary monitor"""
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # Primary monitor
                screenshot = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
                self.current_screenshot = frame
                self.update_display()
                self.status_label.setText("Screenshot captured")
                # Auto-detect after capture
                self.auto_detect_hp_bar()
        except Exception as e:
            self.status_label.setText(f"Error: {e}")
    
    def auto_detect_hp_bar(self):
        """Automatically detect the HP bar location"""
        if self.current_screenshot is None:
            self.status_label.setText("Take or load a screenshot first")
            return
        
        try:
            frame = self.current_screenshot.copy()
            
            # Convert to HSV for better green text detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Green text color range (adjusted for RotMG's HP text)
            green_lower = np.array([40, 100, 100])
            green_upper = np.array([85, 255, 255])
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            
            # Find contours of green text
            contours, _ = cv2.findContours(
                green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Look for number patterns like "235/235"
            best_region = None
            max_score = 0
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                # Expand region slightly
                x = max(0, x - 5)
                y = max(0, y - 5)
                w = min(frame.shape[1] - x, w + 10)
                h = min(frame.shape[0] - y, h + 10)
                
                region = frame[y:y+h, x:x+w]
                if region.size == 0:
                    continue
                
                # Score based on green density and region shape
                green_region = cv2.inRange(
                    cv2.cvtColor(region, cv2.COLOR_BGR2HSV),
                    green_lower, green_upper
                )
                green_pixels = cv2.countNonZero(green_region)
                region_score = (green_pixels / (w * h)) * (w / max(1, h))
                
                if region_score > max_score:
                    max_score = region_score
                    best_region = (x, y, w, h)
            
            if best_region:
                x, y, w, h = best_region
                # Update spinboxes
                self.x_spin.setValue(x)
                self.y_spin.setValue(y)
                self.width_spin.setValue(w)
                self.height_spin.setValue(h)
                self.update_display()
                self.status_label.setText("HP bar auto-detected")
            else:
                self.status_label.setText("Could not auto-detect HP bar")
        
        except Exception as e:
            self.status_label.setText(f"Auto-detection failed: {e}")
    
    def update_display(self):
        """Update the display with current screenshot and HP bar overlay"""
        if self.current_screenshot is None:
            return
        
        try:
            frame = self.current_screenshot.copy()
            
            # Draw HP bar region rectangle
            x = int(self.x_spin.value())
            y = int(self.y_spin.value())
            width = int(self.width_spin.value())
            height = int(self.height_spin.value())

            # Clamp to image bounds to avoid errors
            h_img, w_img = frame.shape[:2]
            x = max(0, min(x, w_img - 1))
            y = max(0, min(y, h_img - 1))
            width = max(1, min(width, w_img - x))
            height = max(1, min(height, h_img - y))

            # Semi-transparent filled overlay to visually encapsulate the region
            overlay = frame.copy()
            cv2.rectangle(overlay, (x, y), (x + width, y + height), (0, 255, 0), -1)
            alpha = 0.25
            frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

            # Bright border for clarity
            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)

            # Small label with coordinates and size
            label = f"x:{x} y:{y} w:{width} h:{height}"
            txt_org = (x, max(0, y - 6))
            cv2.putText(frame, label, txt_org, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            
            # Convert to QPixmap for display
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(
                frame.data, width, height, bytes_per_line, 
                QImage.Format_RGB888
            ).rgbSwapped()
            pixmap = QPixmap.fromImage(q_image)
            
            # Scale to fit display
            scaled_pixmap = pixmap.scaled(
                800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.screenshot_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.status_label.setText(f"Display update failed: {e}")
    
    def save_config(self):
        """Save the current configuration"""
        try:
            config_path = "config/user_config.json"
            
            # Load existing config
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Update HP bar region
            config['hp_bar_region'] = {
                'x': self.x_spin.value(),
                'y': self.y_spin.value(),
                'width': self.width_spin.value(),
                'height': self.height_spin.value()
            }
            
            # Save config
            os.makedirs("config", exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.status_label.setText("Configuration saved!")
            QMessageBox.information(
                self, "Success", 
                "HP bar configuration saved successfully!"
            )
            
        except Exception as e:
            self.status_label.setText(f"Error saving config: {e}")
            QMessageBox.warning(
                self, "Error", 
                f"Failed to save configuration: {e}"
            )
    
    def test_hp_detection(self):
        """Test HP detection with current settings"""
        if self.current_screenshot is None:
            self.status_label.setText("Please capture or load a screenshot first")
            return
        
        try:
            # Extract HP bar region
            x = self.x_spin.value()
            y = self.y_spin.value()
            width = self.width_spin.value()
            height = self.height_spin.value()
            
            hp_region = self.current_screenshot[y:y+height, x:x+width]
            
            if hp_region.size == 0:
                self.status_label.setText("Invalid region - no pixels found")
                return
            
            # Convert to HSV and measure green content
            hsv = cv2.cvtColor(hp_region, cv2.COLOR_BGR2HSV)
            
            # Green text range
            green_lower = np.array([40, 100, 100])
            green_upper = np.array([85, 255, 255])
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            
            # Calculate percentage of green pixels
            green_pixels = cv2.countNonZero(green_mask)
            total_pixels = hp_region.shape[0] * hp_region.shape[1]
            green_percent = (green_pixels / total_pixels) * 100
            
            # Try OCR if available
            try:
                import pytesseract
                from PIL import Image

                # Prepare image for OCR
                gray = cv2.cvtColor(hp_region, cv2.COLOR_BGR2GRAY)
                gray = cv2.convertScaleAbs(gray, alpha=2.0, beta=0)
                _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
                kernel = np.ones((1, 1), np.uint8)
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                thresh = cv2.resize(thresh, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

                # Run OCR
                pil_image = Image.fromarray(thresh)
                ocr_text = pytesseract.image_to_string(
                    pil_image,
                    config='--psm 7 -c tessedit_char_whitelist=0123456789/()+-'
                ).strip()

                self.status_label.setText(
                    f"Test Results:\n"
                    f"Green pixels: {green_percent:.1f}%\n"
                    f"OCR text: '{ocr_text}'"
                )
            except (ImportError, _TessErr):
                self.status_label.setText(
                    f"Test Results:\n"
                    f"Green pixels: {green_percent:.1f}%\n"
                    f"OCR not available (Tesseract not installed/in PATH)"
                )
            
        except Exception as e:
            self.status_label.setText(f"Error testing HP detection: {e}")

def main():
    """Run the calibration tool"""
    import sys
    app = QApplication(sys.argv)
    window = HPCalibrator()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()