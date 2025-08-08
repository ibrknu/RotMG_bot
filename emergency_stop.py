#!/usr/bin/env python3
"""
Emergency stop script to force stop any running bot processes
"""
import os
import sys
import psutil
import time

def find_and_kill_bot_processes():
    """Find and kill any running bot processes."""
    print("=== Emergency Bot Stop ===\n")
    
    killed_processes = []
    
    # Look for Python processes that might be running the bot
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('bot' in arg.lower() for arg in cmdline):
                print(f"Found bot process: PID {proc.info['pid']} - {cmdline}")
                proc.terminate()
                killed_processes.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Also look for Python processes with our specific files
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('main.py' in arg or 'simple_bot.py' in arg for arg in cmdline):
                print(f"Found bot process: PID {proc.info['pid']} - {cmdline}")
                proc.terminate()
                killed_processes.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Wait a moment and force kill if needed
    time.sleep(1)
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] in killed_processes:
                if proc.is_running():
                    print(f"Force killing process: PID {proc.info['pid']}")
                    proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if killed_processes:
        print(f"\n✅ Killed {len(killed_processes)} bot processes")
    else:
        print("\nℹ️  No bot processes found")
    
    return len(killed_processes) > 0

def main():
    """Run the emergency stop."""
    try:
        success = find_and_kill_bot_processes()
        if success:
            print("\n✅ Emergency stop completed successfully!")
        else:
            print("\nℹ️  No bot processes were running")
    except Exception as e:
        print(f"\n❌ Error during emergency stop: {e}")

if __name__ == "__main__":
    main() 