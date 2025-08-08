#!/usr/bin/env python3
"""
Vision Calibration Tool for RotMG Bot
Interactive tool for calibrating vision detection parameters
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from pathlib import Path
import logging
from vision.detection import capture_screen, find_enemies, find_bullets, find_loot, get_hp_percent
from vision.asset_loader import AssetLoader

class VisionCalibrationTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RotMG Bot - Vision Calibration Tool")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.asset_loader = AssetLoader("assets")
        self.current_frame = None
        self.calibration_data = {}
        self.load_calibration_data()
        
        self.setup_ui()
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the calibration tool"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/calibration.log'),
                logging.StreamHandler()
            ]
        )
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Control panel (left side)
        self.setup_control_panel(main_frame)
        
        # Image display (right side)
        self.setup_image_display(main_frame)
        
        # Status bar
        self.setup_status_bar(main_frame)
        
    def setup_control_panel(self, parent):
        """Setup the control panel with buttons and settings"""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="5")
        control_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Capture buttons
        ttk.Button(control_frame, text="Capture Screen", command=self.capture_screen).grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(control_frame, text="Load Image", command=self.load_image).grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(control_frame, text="Save Calibration", command=self.save_calibration).grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Detection toggles
        detection_frame = ttk.LabelFrame(control_frame, text="Detection Features", padding="5")
        detection_frame.grid(row=3, column=0, pady=10, sticky=(tk.W, tk.E))
        
        self.hp_detection_var = tk.BooleanVar(value=True)
        self.enemy_detection_var = tk.BooleanVar(value=True)
        self.bullet_detection_var = tk.BooleanVar(value=True)
        self.loot_detection_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(detection_frame, text="HP Detection", variable=self.hp_detection_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(detection_frame, text="Enemy Detection", variable=self.enemy_detection_var).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(detection_frame, text="Bullet Detection", variable=self.bullet_detection_var).grid(row=2, column=0, sticky=tk.W)
        ttk.Checkbutton(detection_frame, text="Loot Detection", variable=self.loot_detection_var).grid(row=3, column=0, sticky=tk.W)
        
        # HP Bar calibration
        hp_frame = ttk.LabelFrame(control_frame, text="HP Bar Calibration", padding="5")
        hp_frame.grid(row=4, column=0, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Label(hp_frame, text="X1:").grid(row=0, column=0, sticky=tk.W)
        self.hp_x1_var = tk.IntVar(value=50)
        ttk.Entry(hp_frame, textvariable=self.hp_x1_var, width=8).grid(row=0, column=1, padx=5)
        
        ttk.Label(hp_frame, text="Y1:").grid(row=1, column=0, sticky=tk.W)
        self.hp_y1_var = tk.IntVar(value=900)
        ttk.Entry(hp_frame, textvariable=self.hp_y1_var, width=8).grid(row=1, column=1, padx=5)
        
        ttk.Label(hp_frame, text="X2:").grid(row=2, column=0, sticky=tk.W)
        self.hp_x2_var = tk.IntVar(value=250)
        ttk.Entry(hp_frame, textvariable=self.hp_x2_var, width=8).grid(row=2, column=1, padx=5)
        
        ttk.Label(hp_frame, text="Y2:").grid(row=3, column=0, sticky=tk.W)
        self.hp_y2_var = tk.IntVar(value=920)
        ttk.Entry(hp_frame, textvariable=self.hp_y2_var, width=8).grid(row=3, column=1, padx=5)
        
        ttk.Button(hp_frame, text="Test HP Detection", command=self.test_hp_detection).grid(row=4, column=0, columnspan=2, pady=5)
        
        # Detection thresholds
        threshold_frame = ttk.LabelFrame(control_frame, text="Detection Thresholds", padding="5")
        threshold_frame.grid(row=5, column=0, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Label(threshold_frame, text="Template Match Threshold:").grid(row=0, column=0, sticky=tk.W)
        self.template_threshold_var = tk.DoubleVar(value=0.8)
        ttk.Scale(threshold_frame, from_=0.1, to=1.0, variable=self.template_threshold_var, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(threshold_frame, text="HP Red Threshold:").grid(row=1, column=0, sticky=tk.W)
        self.hp_red_threshold_var = tk.IntVar(value=150)
        ttk.Scale(threshold_frame, from_=0, to=255, variable=self.hp_red_threshold_var, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky=(tk.W, tk.E))
        
    def setup_image_display(self, parent):
        """Setup the image display area"""
        display_frame = ttk.LabelFrame(parent, text="Image Display", padding="5")
        display_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # Canvas for image display
        self.canvas = tk.Canvas(display_frame, bg="black")
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Bind mouse events for coordinate selection
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        
    def setup_status_bar(self, parent):
        """Setup the status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.coord_label = ttk.Label(status_frame, text="")
        self.coord_label.grid(row=0, column=1, sticky=tk.E)
        
    def capture_screen(self):
        """Capture the current screen"""
        try:
            self.current_frame = capture_screen()
            self.display_image(self.current_frame)
            self.update_status("Screen captured successfully")
            logging.info("Screen captured")
        except Exception as e:
            self.update_status(f"Failed to capture screen: {e}")
            logging.error(f"Screen capture failed: {e}")
            
    def load_image(self):
        """Load an image file"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if file_path:
            try:
                self.current_frame = cv2.imread(file_path)
                self.display_image(self.current_frame)
                self.update_status(f"Loaded image: {os.path.basename(file_path)}")
                logging.info(f"Loaded image: {file_path}")
            except Exception as e:
                self.update_status(f"Failed to load image: {e}")
                logging.error(f"Image load failed: {e}")
                
    def display_image(self, image):
        """Display image on canvas with detection overlays"""
        if image is None:
            return
            
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Apply detection overlays
        display_image = image_rgb.copy()
        
        if self.hp_detection_var.get():
            self.draw_hp_bar(display_image)
            
        if self.enemy_detection_var.get():
            self.draw_enemy_detections(display_image)
            
        if self.bullet_detection_var.get():
            self.draw_bullet_detections(display_image)
            
        if self.loot_detection_var.get():
            self.draw_loot_detections(display_image)
        
        # Convert to PhotoImage for tkinter
        height, width = display_image.shape[:2]
        
        # Resize if too large
        max_size = 800
        if width > max_size or height > max_size:
            scale = min(max_size / width, max_size / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            display_image = cv2.resize(display_image, (new_width, new_height))
            height, width = new_height, new_width
        
        # Convert to PhotoImage
        image_pil = Image.fromarray(display_image)
        self.photo = ImageTk.PhotoImage(image_pil)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def draw_hp_bar(self, image):
        """Draw HP bar detection overlay"""
        x1, y1 = self.hp_x1_var.get(), self.hp_y1_var.get()
        x2, y2 = self.hp_x2_var.get(), self.hp_y2_var.get()
        
        # Draw rectangle around HP bar
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Calculate and display HP percentage
        if self.current_frame is not None:
            hp_percent = get_hp_percent(self.current_frame)
            if hp_percent is not None:
                cv2.putText(image, f"HP: {hp_percent}%", (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
    def draw_enemy_detections(self, image):
        """Draw enemy detection overlays"""
        if self.current_frame is None:
            return
            
        enemies = find_enemies(self.current_frame)
        for enemy in enemies:
            x, y = enemy['center']
            cv2.circle(image, (x, y), 20, (0, 0, 255), 2)
            cv2.putText(image, enemy['name'], (x+25, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                       
    def draw_bullet_detections(self, image):
        """Draw bullet detection overlays"""
        if self.current_frame is None:
            return
            
        bullets = find_bullets(self.current_frame)
        for bullet in bullets:
            x, y = bullet['center']
            cv2.circle(image, (x, y), 5, (255, 0, 0), 2)
            
    def draw_loot_detections(self, image):
        """Draw loot detection overlays"""
        if self.current_frame is None:
            return
            
        loot_items = find_loot(self.current_frame)
        for item in loot_items:
            x, y = item['center']
            cv2.circle(image, (x, y), 15, (0, 255, 255), 2)
            cv2.putText(image, item['name'], (x+20, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                       
    def test_hp_detection(self):
        """Test HP detection with current settings"""
        if self.current_frame is None:
            messagebox.showwarning("No Image", "Please capture or load an image first")
            return
            
        try:
            hp_percent = get_hp_percent(self.current_frame)
            if hp_percent is not None:
                messagebox.showinfo("HP Detection Test", f"Detected HP: {hp_percent}%")
                self.update_status(f"HP Detection: {hp_percent}%")
            else:
                messagebox.showwarning("HP Detection Test", "Could not detect HP")
                self.update_status("HP Detection: Failed")
        except Exception as e:
            messagebox.showerror("HP Detection Test", f"Error: {e}")
            self.update_status(f"HP Detection Error: {e}")
            
    def on_canvas_click(self, event):
        """Handle canvas click for coordinate selection"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.coord_label.config(text=f"Click: ({int(x)}, {int(y)})")
        
    def on_canvas_drag(self, event):
        """Handle canvas drag for rectangle selection"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.coord_label.config(text=f"Drag: ({int(x)}, {int(y)})")
        
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def load_calibration_data(self):
        """Load existing calibration data"""
        calib_file = Path("config/calibration.json")
        if calib_file.exists():
            try:
                with open(calib_file, 'r') as f:
                    self.calibration_data = json.load(f)
                logging.info("Loaded existing calibration data")
            except Exception as e:
                logging.error(f"Failed to load calibration data: {e}")
                self.calibration_data = {}
        else:
            self.calibration_data = {}
            
    def save_calibration(self):
        """Save current calibration settings"""
        try:
            # Create config directory if it doesn't exist
            os.makedirs("config", exist_ok=True)
            
            # Save calibration data
            calib_data = {
                "hp_bar": {
                    "x1": self.hp_x1_var.get(),
                    "y1": self.hp_y1_var.get(),
                    "x2": self.hp_x2_var.get(),
                    "y2": self.hp_y2_var.get()
                },
                "thresholds": {
                    "template_match": self.template_threshold_var.get(),
                    "hp_red": self.hp_red_threshold_var.get()
                },
                "detection_features": {
                    "hp_detection": self.hp_detection_var.get(),
                    "enemy_detection": self.enemy_detection_var.get(),
                    "bullet_detection": self.bullet_detection_var.get(),
                    "loot_detection": self.loot_detection_var.get()
                }
            }
            
            with open("config/calibration.json", 'w') as f:
                json.dump(calib_data, f, indent=2)
                
            self.update_status("Calibration saved successfully")
            logging.info("Calibration data saved")
            messagebox.showinfo("Success", "Calibration settings saved!")
            
        except Exception as e:
            self.update_status(f"Failed to save calibration: {e}")
            logging.error(f"Failed to save calibration: {e}")
            messagebox.showerror("Error", f"Failed to save calibration: {e}")
            
    def run(self):
        """Start the calibration tool"""
        self.root.mainloop()

if __name__ == "__main__":
    # Import required modules for image display
    try:
        from PIL import Image, ImageTk
    except ImportError:
        print("PIL/Pillow is required for image display. Install with: pip install Pillow")
        exit(1)
        
    app = VisionCalibrationTool()
    app.run() 