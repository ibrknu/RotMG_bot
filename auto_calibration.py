#!/usr/bin/env python3
"""
Automatic Calibration Tool for RotMG Bot
Automatically detects UI elements from uploaded screenshots
"""

import cv2
import numpy as np
import json
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoCalibrationTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RotMG Bot - Automatic Calibration")
        self.root.geometry("1000x700")
        
        self.current_image = None
        self.detected_regions = {}
        
        self.setup_ui()
        
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
        """Setup the control panel"""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="5")
        control_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Upload screenshot button
        ttk.Button(control_frame, text="Upload Screenshot", command=self.upload_screenshot).grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Auto-detect button
        ttk.Button(control_frame, text="Auto-Detect UI Elements", command=self.auto_detect_ui).grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Manual adjustment section
        manual_frame = ttk.LabelFrame(control_frame, text="Manual Adjustments", padding="5")
        manual_frame.grid(row=2, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # HP Bar coordinates
        ttk.Label(manual_frame, text="HP Bar:").grid(row=0, column=0, sticky=tk.W)
        
        hp_frame = ttk.Frame(manual_frame)
        hp_frame.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(hp_frame, text="X1:").grid(row=0, column=0, sticky=tk.W)
        self.hp_x1_var = tk.IntVar(value=50)
        ttk.Entry(hp_frame, textvariable=self.hp_x1_var, width=6).grid(row=0, column=1, padx=2)
        
        ttk.Label(hp_frame, text="Y1:").grid(row=0, column=2, sticky=tk.W)
        self.hp_y1_var = tk.IntVar(value=900)
        ttk.Entry(hp_frame, textvariable=self.hp_y1_var, width=6).grid(row=0, column=3, padx=2)
        
        ttk.Label(hp_frame, text="X2:").grid(row=1, column=0, sticky=tk.W)
        self.hp_x2_var = tk.IntVar(value=250)
        ttk.Entry(hp_frame, textvariable=self.hp_x2_var, width=6).grid(row=1, column=1, padx=2)
        
        ttk.Label(hp_frame, text="Y2:").grid(row=1, column=2, sticky=tk.W)
        self.hp_y2_var = tk.IntVar(value=920)
        ttk.Entry(hp_frame, textvariable=self.hp_y2_var, width=6).grid(row=1, column=3, padx=2)
        
        # Test and Save buttons
        ttk.Button(manual_frame, text="Test HP Detection", command=self.test_hp_detection).grid(row=2, column=0, columnspan=4, pady=5)
        ttk.Button(manual_frame, text="Save Calibration", command=self.save_calibration).grid(row=3, column=0, columnspan=4, pady=5)
        
        # Detection results
        results_frame = ttk.LabelFrame(control_frame, text="Detection Results", padding="5")
        results_frame.grid(row=3, column=0, pady=10, sticky=(tk.W, tk.E))
        
        self.results_text = tk.Text(results_frame, height=8, width=30)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
    def setup_image_display(self, parent):
        """Setup the image display area"""
        display_frame = ttk.LabelFrame(parent, text="Screenshot Display", padding="5")
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
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
    def setup_status_bar(self, parent):
        """Setup the status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready - Upload a screenshot to begin")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.coord_label = ttk.Label(status_frame, text="")
        self.coord_label.grid(row=0, column=1, sticky=tk.E)
        
    def upload_screenshot(self):
        """Upload a screenshot file"""
        file_path = filedialog.askopenfilename(
            title="Select Screenshot",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if file_path:
            try:
                # Load image
                self.current_image = cv2.imread(file_path)
                if self.current_image is None:
                    raise ValueError("Failed to load image")
                
                self.display_image(self.current_image)
                self.update_status(f"Loaded: {os.path.basename(file_path)} ({self.current_image.shape[1]}x{self.current_image.shape[0]})")
                
                # Auto-detect UI elements
                self.auto_detect_ui()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")
                self.update_status(f"Error loading image: {e}")
    
    def auto_detect_ui(self):
        """Automatically detect UI elements in the image"""
        if self.current_image is None:
            messagebox.showwarning("No Image", "Please upload a screenshot first")
            return
        
        self.update_status("Auto-detecting UI elements...")
        self.results_text.delete(1.0, tk.END)
        
        try:
            # Convert to different color spaces for detection
            hsv = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            
            detected_regions = {}
            
            # 1. Detect HP bar (look for red regions at bottom of screen)
            hp_regions = self.detect_hp_bar(hsv)
            if hp_regions:
                detected_regions['hp_bar'] = hp_regions[0]  # Take the largest red region
                self.results_text.insert(tk.END, f"✅ HP Bar detected: {hp_regions[0]}\n")
            
            # 2. Detect UI panels (look for dark rectangular regions)
            ui_panels = self.detect_ui_panels(gray)
            if ui_panels:
                detected_regions['ui_panels'] = ui_panels
                self.results_text.insert(tk.END, f"✅ UI Panels detected: {len(ui_panels)} regions\n")
            
            # 3. Detect potential enemy regions (look for bright moving objects)
            enemy_regions = self.detect_potential_enemies(gray)
            if enemy_regions:
                detected_regions['enemy_regions'] = enemy_regions
                self.results_text.insert(tk.END, f"✅ Potential enemies: {len(enemy_regions)} regions\n")
            
            # 4. Detect inventory area (look for grid-like patterns)
            inventory_regions = self.detect_inventory_area(gray)
            if inventory_regions:
                detected_regions['inventory'] = inventory_regions
                self.results_text.insert(tk.END, f"✅ Inventory area detected\n")
            
            self.detected_regions = detected_regions
            
            # Update manual coordinates if HP bar was detected
            if 'hp_bar' in detected_regions:
                x1, y1, x2, y2 = detected_regions['hp_bar']
                self.hp_x1_var.set(x1)
                self.hp_y1_var.set(y1)
                self.hp_x2_var.set(x2)
                self.hp_y2_var.set(y2)
            
            # Draw detected regions on image
            self.draw_detected_regions()
            
            self.update_status("Auto-detection completed")
            
        except Exception as e:
            self.update_status(f"Auto-detection error: {e}")
            messagebox.showerror("Error", f"Auto-detection failed: {e}")
    
    def detect_hp_bar(self, hsv_image):
        """Detect HP bar by looking for red regions"""
        # Define red color range (HP bars are typically red)
        red_lower1 = np.array([0, 100, 100])
        red_upper1 = np.array([10, 255, 255])
        red_lower2 = np.array([160, 100, 100])
        red_upper2 = np.array([180, 255, 255])
        
        # Create masks for red regions
        mask1 = cv2.inRange(hsv_image, red_lower1, red_upper1)
        mask2 = cv2.inRange(hsv_image, red_lower2, red_upper2)
        red_mask = mask1 + mask2
        
        # Find contours in red regions
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        hp_regions = []
        h, w = hsv_image.shape[:2]
        
        for contour in contours:
            # Filter by size and position
            area = cv2.contourArea(contour)
            if area > 1000 and area < 50000:  # Reasonable size for HP bar
                x, y, w_contour, h_contour = cv2.boundingRect(contour)
                
                # HP bar is typically at bottom of screen and wider than tall
                if y > h * 0.7 and w_contour > h_contour * 2:
                    hp_regions.append((x, y, x + w_contour, y + h_contour))
        
        # Sort by area (largest first)
        hp_regions.sort(key=lambda r: (r[2]-r[0])*(r[3]-r[1]), reverse=True)
        return hp_regions
    
    def detect_ui_panels(self, gray_image):
        """Detect UI panels by looking for dark rectangular regions"""
        # Apply threshold to find dark regions
        _, thresh = cv2.threshold(gray_image, 50, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        ui_panels = []
        h, w = gray_image.shape
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 5000:  # Minimum size for UI panel
                x, y, w_contour, h_contour = cv2.boundingRect(contour)
                
                # UI panels are typically rectangular and at edges
                aspect_ratio = w_contour / h_contour
                if 0.5 < aspect_ratio < 3.0:  # Reasonable aspect ratio
                    ui_panels.append((x, y, x + w_contour, y + h_contour))
        
        return ui_panels
    
    def detect_potential_enemies(self, gray_image):
        """Detect potential enemies by looking for bright moving objects"""
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
        
        # Apply threshold to find bright objects
        _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        enemy_regions = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 10000:  # Reasonable size for enemies
                x, y, w_contour, h_contour = cv2.boundingRect(contour)
                
                # Enemies are typically in the center area of the screen
                center_x = x + w_contour // 2
                center_y = y + h_contour // 2
                
                if 0.2 < center_x / gray_image.shape[1] < 0.8 and 0.2 < center_y / gray_image.shape[0] < 0.8:
                    enemy_regions.append((x, y, x + w_contour, y + h_contour))
        
        return enemy_regions
    
    def detect_inventory_area(self, gray_image):
        """Detect inventory area by looking for grid-like patterns"""
        # Apply edge detection
        edges = cv2.Canny(gray_image, 50, 150)
        
        # Look for horizontal and vertical lines
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=30, maxLineGap=10)
        
        if lines is not None:
            # Count horizontal and vertical lines
            horizontal_lines = 0
            vertical_lines = 0
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(x2 - x1) > abs(y2 - y1):  # Horizontal line
                    horizontal_lines += 1
                else:  # Vertical line
                    vertical_lines += 1
            
            # If we have a grid-like pattern, look for the inventory area
            if horizontal_lines > 3 and vertical_lines > 3:
                # Inventory is typically on the right side
                h, w = gray_image.shape
                return [(int(w * 0.7), int(h * 0.3), w, int(h * 0.8))]
        
        return []
    
    def draw_detected_regions(self):
        """Draw detected regions on the displayed image"""
        if self.current_image is None:
            return
        
        # Create a copy for drawing
        display_image = self.current_image.copy()
        
        # Draw HP bar region
        if 'hp_bar' in self.detected_regions:
            x1, y1, x2, y2 = self.detected_regions['hp_bar']
            cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(display_image, "HP Bar", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw UI panels
        if 'ui_panels' in self.detected_regions:
            for i, (x1, y1, x2, y2) in enumerate(self.detected_regions['ui_panels']):
                cv2.rectangle(display_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(display_image, f"UI Panel {i+1}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        # Draw potential enemies
        if 'enemy_regions' in self.detected_regions:
            for i, (x1, y1, x2, y2) in enumerate(self.detected_regions['enemy_regions']):
                cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(display_image, f"Enemy {i+1}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # Draw inventory area
        if 'inventory' in self.detected_regions:
            for x1, y1, x2, y2 in self.detected_regions['inventory']:
                cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 255, 255), 2)
                cv2.putText(display_image, "Inventory", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        self.display_image(display_image)
    
    def display_image(self, image):
        """Display image on canvas"""
        if image is None:
            return
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize if too large
        height, width = image_rgb.shape[:2]
        max_size = 600
        
        if width > max_size or height > max_size:
            scale = min(max_size / width, max_size / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image_rgb = cv2.resize(image_rgb, (new_width, new_height))
        
        # Convert to PhotoImage
        image_pil = Image.fromarray(image_rgb)
        self.photo = ImageTk.PhotoImage(image_pil)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_click(self, event):
        """Handle canvas click for coordinate selection"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.coord_label.config(text=f"Click: ({int(x)}, {int(y)})")
    
    def test_hp_detection(self):
        """Test HP detection with current coordinates"""
        if self.current_image is None:
            messagebox.showwarning("No Image", "Please upload a screenshot first")
            return
        
        try:
            x1, y1 = self.hp_x1_var.get(), self.hp_y1_var.get()
            x2, y2 = self.hp_x2_var.get(), self.hp_y2_var.get()
            
            # Ensure coordinates are within image bounds
            h, w = self.current_image.shape[:2]
            x1 = max(0, min(x1, w-1))
            y1 = max(0, min(y1, h-1))
            x2 = max(0, min(x2, w-1))
            y2 = max(0, min(y2, h-1))
            
            # Extract HP bar region
            hp_region = self.current_image[y1:y2, x1:x2]
            
            if hp_region.size == 0:
                messagebox.showwarning("Invalid Region", "HP bar region is empty")
                return
            
            # Convert to HSV and detect red
            hsv = cv2.cvtColor(hp_region, cv2.COLOR_BGR2HSV)
            red_lower = np.array([0, 100, 100])
            red_upper = np.array([10, 255, 255])
            mask = cv2.inRange(hsv, red_lower, red_upper)
            
            # Calculate HP percentage
            red_pixels = cv2.countNonZero(mask)
            total_pixels = hp_region.shape[0] * hp_region.shape[1]
            hp_percent = int((red_pixels / total_pixels) * 100) if total_pixels > 0 else 0
            
            messagebox.showinfo("HP Detection Test", f"Detected HP: {hp_percent}%\nRed pixels: {red_pixels}/{total_pixels}")
            self.results_text.insert(tk.END, f"HP Test: {hp_percent}% ({red_pixels}/{total_pixels} pixels)\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"HP detection test failed: {e}")
    
    def save_calibration(self):
        """Save calibration settings"""
        try:
            # Create config directory
            os.makedirs("config", exist_ok=True)
            
            # Prepare calibration data
            calib_data = {
                "hp_bar": {
                    "x1": self.hp_x1_var.get(),
                    "y1": self.hp_y1_var.get(),
                    "x2": self.hp_x2_var.get(),
                    "y2": self.hp_y2_var.get()
                },
                "thresholds": {
                    "template_match": 0.8,
                    "hp_red": 100
                },
                "detection_features": {
                    "hp_detection": True,
                    "enemy_detection": True,
                    "bullet_detection": True,
                    "loot_detection": True
                },
                "auto_detected_regions": self.detected_regions
            }
            
            # Save to file
            with open("config/calibration.json", 'w') as f:
                json.dump(calib_data, f, indent=2)
            
            self.update_status("Calibration saved successfully")
            messagebox.showinfo("Success", "Calibration settings saved!\n\nYou can now run the bot with: python main.py")
            
        except Exception as e:
            self.update_status(f"Failed to save calibration: {e}")
            messagebox.showerror("Error", f"Failed to save calibration: {e}")
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def run(self):
        """Start the calibration tool"""
        self.root.mainloop()

if __name__ == "__main__":
    app = AutoCalibrationTool()
    app.run() 