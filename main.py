#!/usr/bin/env python3
"""
YouTube to MP3 Downloader - Entry Point
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ui import MainWindow
    import tkinter as tk
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def main():
    root = tk.Tk()
    root.title("YouTube to MP3 Downloader")
    root.geometry("800x600")
    root.minsize(700, 500)
    root.configure(bg="#2b2b2b")
    
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()