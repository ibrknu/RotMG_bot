#!/usr/bin/env python3
"""
Screenshot-based Calibration Tool for RotMG Bot
Automatically detects UI elements from uploaded screenshots
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScreenshotCalibrationTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RotMG Bot - Screenshot Calibration")
        self.root.geometry("1000x700")
        
        self.screenshot = None
        self.calibration_data = {}
        
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
        
        # Load screenshot button
        ttk.Button(control_frame, text="Load Screenshot", command=self.load_screenshot).grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Auto-detect button
        ttk.Button(control_frame, text="Auto-Detect UI Elements", command=self.auto_detect_ui).grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Manual calibration
        ttk.Button(control_frame, text="Manual HP Bar Selection", command=self.manual_hp_selection).grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Save calibration
        ttk.Button(control_frame, text="Save Calibration", command=self.save_calibration).grid(row=3, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Test calibration
        ttk.Button(control_frame, text="Test Calibration", command=self.test_calibration).grid(row=4, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Results display
        results_frame = ttk.LabelFrame(control_frame, text="Detection Results", padding="5")
        results_frame.grid(row=5, column=0, pady=10, sticky=(tk.W, tk.E))
        
        self.results_text = tk.Text(results_frame, height=10, width=30)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
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
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Selection variables
        self.selection_start = None
        self.selection_rect = None
        
    def setup_status_bar(self, parent):
        """Setup the status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready - Load a screenshot to begin")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.coord_label = ttk.Label(status_frame, text="")
        self.coord_label.grid(row=0, column=1, sticky=tk.E)
        
    def load_screenshot(self):
        """Load a screenshot file"""
        file_path = filedialog.askopenfilename(
            title="Select Screenshot",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if file_path:
            try:
                self.screenshot = cv2.imread(file_path)
                if self.screenshot is not None:
                    self.display_image(self.screenshot)
                    self.update_status(f"Loaded: {os.path.basename(file_path)} ({self.screenshot.shape[1]}x{self.screenshot.shape[0]})")
                    self.results_text.delete(1.0, tk.END)
                    self.results_text.insert(tk.END, "Screenshot loaded successfully.\nClick 'Auto-Detect UI Elements' to begin analysis.\n")
                else:
                    messagebox.showerror("Error", "Failed to load image")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")
                
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
            self.scale_factor = scale
        else:
            self.scale_factor = 1.0
        
        # Convert to PhotoImage
        from PIL import Image, ImageTk
        image_pil = Image.fromarray(image_rgb)
        self.photo = ImageTk.PhotoImage(image_pil)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def auto_detect_ui(self):
        """Automatically detect UI elements in the screenshot"""
        if self.screenshot is None:
            messagebox.showwarning("No Screenshot", "Please load a screenshot first")
            return
            
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Auto-detecting UI elements...\n\n")
        
        try:
            # Detect HP bar (look for red horizontal bars)
            hp_regions = self.detect_hp_bars()
            
            # Detect UI elements (look for rectangular regions)
            ui_regions = self.detect_ui_regions()
            
            # Display results
            self.results_text.insert(tk.END, f"HP Bar Candidates: {len(hp_regions)}\n")
            for i, region in enumerate(hp_regions):
                self.results_text.insert(tk.END, f"  {i+1}. x={region[0]}, y={region[1]}, w={region[2]}, h={region[3]}\n")
            
            self.results_text.insert(tk.END, f"\nUI Regions Found: {len(ui_regions)}\n")
            
            # Store best HP bar candidate
            if hp_regions:
                best_hp = hp_regions[0]  # Take the first (usually the most prominent)
                self.calibration_data['hp_bar'] = {
                    'x1': best_hp[0],
                    'y1': best_hp[1],
                    'x2': best_hp[0] + best_hp[2],
                    'y2': best_hp[1] + best_hp[3]
                }
                self.results_text.insert(tk.END, f"\n✅ HP Bar auto-detected and saved!\n")
            
            self.update_status("Auto-detection completed")
            
        except Exception as e:
            self.results_text.insert(tk.END, f"Error during auto-detection: {e}\n")
            logger.error(f"Auto-detection error: {e}")
            
    def detect_hp_bars(self):
        """Detect potential HP bars by looking for red horizontal regions"""
        if self.screenshot is None:
            return []
            
        # Convert to HSV
        hsv = cv2.cvtColor(self.screenshot, cv2.COLOR_BGR2HSV)
        
        # Define red color range
        red_lower1 = np.array([0, 100, 100])
        red_upper1 = np.array([10, 255, 255])
        red_lower2 = np.array([160, 100, 100])
        red_upper2 = np.array([180, 255, 255])
        
        # Create masks for red
        mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
        mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
        red_mask = mask1 + mask2
        
        # Find contours
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        hp_candidates = []
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by size and aspect ratio (HP bars are usually wide and short)
            if w > 100 and h < 50 and w > h * 2:
                # Check if it's in the bottom area (typical HP bar location)
                if y > self.screenshot.shape[0] * 0.7:  # Bottom 30% of screen
                    hp_candidates.append((x, y, w, h))
        
        # Sort by area (largest first)
        hp_candidates.sort(key=lambda x: x[2] * x[3], reverse=True)
        
        return hp_candidates[:3]  # Return top 3 candidates
        
    def detect_ui_regions(self):
        """Detect UI regions by looking for rectangular areas"""
        if self.screenshot is None:
            return []
            
        # Convert to grayscale
        gray = cv2.cvtColor(self.screenshot, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        ui_regions = []
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by size
            if w > 50 and h > 20 and w < 400 and h < 200:
                ui_regions.append((x, y, w, h))
        
        return ui_regions
        
    def manual_hp_selection(self):
        """Allow manual selection of HP bar"""
        if self.screenshot is None:
            messagebox.showwarning("No Screenshot", "Please load a screenshot first")
            return
            
        self.update_status("Click and drag to select HP bar region")
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Manual selection mode:\nClick and drag to select HP bar region\n")
        
    def on_canvas_click(self, event):
        """Handle canvas click for selection"""
        if self.screenshot is None:
            return
            
        # Convert canvas coordinates to image coordinates
        x = int(self.canvas.canvasx(event.x) / self.scale_factor)
        y = int(self.canvas.canvasy(event.y) / self.scale_factor)
        
        self.selection_start = (x, y)
        self.coord_label.config(text=f"Start: ({x}, {y})")
        
    def on_canvas_drag(self, event):
        """Handle canvas drag for selection"""
        if self.selection_start is None or self.screenshot is None:
            return
            
        # Convert canvas coordinates to image coordinates
        x = int(self.canvas.canvasx(event.x) / self.scale_factor)
        y = int(self.canvas.canvasy(event.y) / self.scale_factor)
        
        # Update selection rectangle
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        
        # Draw selection rectangle
        start_x = int(self.selection_start[0] * self.scale_factor)
        start_y = int(self.selection_start[1] * self.scale_factor)
        self.selection_rect = self.canvas.create_rectangle(
            start_x, start_y, event.x, event.y,
            outline="red", width=2
        )
        
        self.coord_label.config(text=f"Selection: ({self.selection_start[0]},{self.selection_start[1]}) to ({x},{y})")
        
    def on_canvas_release(self, event):
        """Handle canvas release to finalize selection"""
        if self.selection_start is None or self.screenshot is None:
            return
            
        # Convert canvas coordinates to image coordinates
        x = int(self.canvas.canvasx(event.x) / self.scale_factor)
        y = int(self.canvas.canvasy(event.y) / self.scale_factor)
        
        # Save HP bar coordinates
        x1, y1 = self.selection_start
        x2, y2 = x, y
        
        # Ensure x1 < x2 and y1 < y2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        
        self.calibration_data['hp_bar'] = {
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2
        }
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"HP Bar manually selected:\n")
        self.results_text.insert(tk.END, f"x1={x1}, y1={y1}, x2={x2}, y2={y2}\n")
        self.results_text.insert(tk.END, f"Width: {x2-x1}, Height: {y2-y1}\n")
        
        self.update_status("HP bar selection completed")
        
    def save_calibration(self):
        """Save calibration data to file"""
        if not self.calibration_data:
            messagebox.showwarning("No Data", "No calibration data to save")
            return
            
        try:
            # Create config directory if it doesn't exist
            os.makedirs("config", exist_ok=True)
            
            # Add default thresholds
            if 'thresholds' not in self.calibration_data:
                self.calibration_data['thresholds'] = {
                    'template_match': 0.8,
                    'hp_red': 150
                }
            
            # Save to file
            with open("config/calibration.json", 'w') as f:
                json.dump(self.calibration_data, f, indent=2)
                
            self.update_status("Calibration saved successfully")
            messagebox.showinfo("Success", "Calibration settings saved!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save calibration: {e}")
            
    def test_calibration(self):
        """Test the current calibration"""
        if not self.calibration_data or 'hp_bar' not in self.calibration_data:
            messagebox.showwarning("No Calibration", "Please detect or select HP bar first")
            return
            
        if self.screenshot is None:
            messagebox.showwarning("No Screenshot", "Please load a screenshot first")
            return
            
        try:
            # Test HP detection
            hp_config = self.calibration_data['hp_bar']
            x1, y1 = hp_config['x1'], hp_config['y1']
            x2, y2 = hp_config['x2'], hp_config['y2']
            
            hp_region = self.screenshot[y1:y2, x1:x2]
            
            # Calculate HP percentage
            hsv = cv2.cvtColor(hp_region, cv2.COLOR_BGR2HSV)
            red_threshold = self.calibration_data.get('thresholds', {}).get('hp_red', 150)
            
            red_lower = np.array([0, red_threshold, 100])
            red_upper = np.array([10, 255, 255])
            mask = cv2.inRange(hsv, red_lower, red_upper)
            
            red_pixels = cv2.countNonZero(mask)
            total_pixels = hp_region.shape[0] * hp_region.shape[1]
            
            if total_pixels > 0:
                hp_percent = int((red_pixels / total_pixels) * 100)
                
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, f"Calibration Test Results:\n\n")
                self.results_text.insert(tk.END, f"HP Region: {x1},{y1} to {x2},{y2}\n")
                self.results_text.insert(tk.END, f"Region Size: {hp_region.shape[1]}x{hp_region.shape[0]}\n")
                self.results_text.insert(tk.END, f"Red Pixels: {red_pixels}/{total_pixels}\n")
                self.results_text.insert(tk.END, f"Detected HP: {hp_percent}%\n")
                
                if hp_percent > 0:
                    self.results_text.insert(tk.END, f"\n✅ HP detection working!\n")
                else:
                    self.results_text.insert(tk.END, f"\n⚠️  No HP detected - check coordinates\n")
            else:
                self.results_text.insert(tk.END, "Error: Invalid HP region\n")
                
        except Exception as e:
            self.results_text.insert(tk.END, f"Test error: {e}\n")
            
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def run(self):
        """Start the calibration tool"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ScreenshotCalibrationTool()
    app.run() 