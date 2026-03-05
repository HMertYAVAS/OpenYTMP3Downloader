#!/usr/bin/env python3
"""
Utility functions and dependency checking
"""
import subprocess
import os
from pathlib import Path
import shutil

def check_dependencies():
    """Check if required tools are installed"""
    missing = []
    
    # Check yt-dlp - use shutil.which which is more reliable
    if not shutil.which("yt-dlp"):
        missing.append("yt-dlp")
    
    # Check ffmpeg
    if not shutil.which("ffmpeg"):
        missing.append("ffmpeg")
    
    return missing

def get_install_instructions():
    """Get installation instructions based on distro"""
    return """INSTALL DEPENDENCIES:

Ubuntu/Debian:
    sudo apt update
    sudo apt install yt-dlp ffmpeg python3-tk

Arch Linux:
    sudo pacman -S yt-dlp ffmpeg python tk

Fedora:
    sudo dnf install yt-dlp ffmpeg python3-tkinter

Or use pip for yt-dlp:
    pip3 install yt-dlp

Then restart this application."""

def ensure_dir(path):
    """Create directory if it doesn't exist"""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

def format_duration(seconds):
    """Format seconds to readable time"""
    if not seconds:
        return "Unknown"
    try:
        seconds = int(seconds)
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        if hours > 0:
            return f"{hours}:{mins:02d}:{secs:02d}"
        return f"{mins}:{secs:02d}"
    except:
        return "Unknown"

def truncate_path(path, length=35):
    """Truncate long paths for display"""
    if len(path) > length:
        return "..." + path[-length:]
    return path