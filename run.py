#!/usr/bin/env python3
import os
import sys
import subprocess

def run_app():
    """
    Simple script to run the RFID Student Wallet Application.
    """
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        # Run the main application directly
        print("Starting RFID Student Wallet Application...")
        subprocess.call([sys.executable, "main.py"])
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Make sure all dependencies are installed.")
        print("Try running: pip install -r requirements.txt")

if __name__ == "__main__":
    run_app() 