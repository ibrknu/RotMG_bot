#!/usr/bin/env python3
"""
Test to show what the bot is detecting in real-time
"""
import time
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(__file__))

def test_detection():
    """Test what the bot is detecting"""
    try:
        from vision import detection
        
        print("Testing bot detection...")
        print("Press Ctrl+C to stop")
        
        while True:
            # Capture screen
            frame = detection.capture_screen()
            print(f"Screen captured: {frame.shape}")
            
            # Test all detection functions
            hp = detection.get_hp_percent(frame)
            enemies = detection.find_enemies(frame)
            bullets = detection.find_bullets(frame)
            loot = detection.find_loot(frame)
            obstacles = detection.find_obstacles(frame)
            
            print(f"HP: {hp}% | Enemies: {len(enemies)} | Bullets: {len(bullets)} | Loot: {len(loot)} | Obstacles: {len(obstacles)}")
            
            if enemies:
                print(f"  Enemies found: {[e['name'] for e in enemies[:3]]}")
            if bullets:
                print(f"  Bullets found: {[b['name'] for b in bullets[:3]]}")
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\nDetection test stopped by user")
    except Exception as e:
        print(f"Detection test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== Bot Detection Test ===")
    print("This will show what the bot is detecting every 2 seconds")
    test_detection() 