#!/usr/bin/env python3
"""
Main UI window and application logic
"""
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import queue
import os
from pathlib import Path

from widgets import ModernButton, ModernEntry, LogText, ProgressBar
from downloader import YouTubeDownloader
from utils import check_dependencies, get_install_instructions, ensure_dir, format_duration, truncate_path

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#2b2b2b")
        
        self.bg_color = "#2b2b2b"
        self.surface_color = "#3b3b3b"
        self.text_color = "#ffffff"
        self.accent_color = "#4a9eff"
        
        self.download_path = str(Path.home() / "Music" / "YouTube_MP3")
        ensure_dir(self.download_path)
        
        self.msg_queue = queue.Queue()
        self.downloader = YouTubeDownloader(ui_callback=self.queue_message)
        self.is_downloading = False
        
        self.build_ui()
        self.check_deps()
        
        # Start queue checker - IMPORTANT
        self.check_queue()
        print("UI Initialized, queue checker started")
        
    def queue_message(self, event_type, message, data):
        """Thread-safe callback"""
        try:
            self.msg_queue.put((event_type, message, data))
            print(f"Queued: {event_type} - {message[:50] if isinstance(message, str) else message}...")
        except Exception as e:
            print(f"Queue error: {e}")
            
    def check_queue(self):
        """Process messages from background thread"""
        try:
            count = 0
            while True:
                try:
                    event_type, message, data = self.msg_queue.get_nowait()
                    self.handle_message(event_type, message, data)
                    count += 1
                except queue.Empty:
                    break
            if count > 0:
                print(f"Processed {count} messages")
        except Exception as e:
            print(f"Check queue error: {e}")
        finally:
            # Schedule next check - THIS IS CRITICAL
            self.root.after(50, self.check_queue)
            
    def handle_message(self, event_type, message, data):
        """Handle messages on main thread"""
        print(f"Handling: {event_type} - {message}")
        try:
            if event_type == "log":
                self.log(message, data)
            elif event_type == "status":
                self.update_status(message, data)
            elif event_type == "done":
                self.download_finished(message)
        except Exception as e:
            print(f"Handle message error: {e}")
            
    def check_deps(self):
        """Check for required dependencies"""
        missing = check_dependencies()
        
        # Debug: print what's happening
        print(f"Dependency check - Missing: {missing}")
        print(f"PATH: {os.environ.get('PATH', 'NOT SET')}")
        
        if missing:
            # Double-check by trying to run the command directly
            for tool in list(missing):
                try:
                    result = subprocess.run([tool, "--version"], 
                                          capture_output=True, timeout=5)
                    if result.returncode == 0:
                        print(f"Found {tool} by direct run, removing from missing")
                        missing.remove(tool)
                except:
                    pass
                    
        if missing:
            self.show_error_dialog(
                "Missing Dependencies",
                f"Required tools not found: {', '.join(missing)}\n\n"
                f"{get_install_instructions()}"
            )
            return False
        return True
            
    def show_error_dialog(self, title, message):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("600x400")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="⚠️ " + title, bg=self.bg_color,
                fg="#f44336", font=("Segoe UI", 16, "bold")).pack(pady=20)
        
        text = tk.Text(dialog, wrap=tk.WORD, bg=self.surface_color,
                      fg=self.text_color, font=("Consolas", 10),
                      padx=15, pady=15, height=12, relief=tk.FLAT)
        text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        text.insert(tk.END, message)
        text.config(state=tk.DISABLED)
        
        ModernButton(dialog, text="OK", command=dialog.destroy,
                    bg_color="#f44336").pack(pady=20)
        
    def build_ui(self):
        main = tk.Frame(self.root, bg=self.bg_color)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.create_header(main)
        self.create_url_section(main)
        self.create_options_section(main)
        self.create_download_button(main)
        self.create_progress_section(main)
        self.create_log_section(main)
        self.create_footer(main)
        
    def create_header(self, parent):
        header = tk.Frame(parent, bg=self.bg_color)
        header.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header, text="🎵 YouTube to MP3 Downloader",
                bg=self.bg_color, fg=self.text_color,
                font=("Segoe UI", 20, "bold")).pack(side=tk.LEFT)
        
    def create_url_section(self, parent):
        frame = tk.LabelFrame(parent, text=" Video URL ", bg=self.bg_color,
                             fg="#888888", font=("Segoe UI", 10),
                             relief=tk.FLAT, bd=2, padx=10, pady=10)
        frame.pack(fill=tk.X, pady=(0, 15))
        frame.config(highlightbackground=self.surface_color, highlightthickness=1)
        
        input_frame = tk.Frame(frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X)
        
        self.url_entry = ModernEntry(input_frame, placeholder="Paste YouTube URL here...", width=50)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ModernButton(input_frame, text="📋 Paste", command=self.paste_url,
                    bg_color="#5a5a5a").pack(side=tk.RIGHT)
        
    def create_options_section(self, parent):
        frame = tk.LabelFrame(parent, text=" Options ", bg=self.bg_color,
                             fg="#888888", font=("Segoe UI", 10),
                             relief=tk.FLAT, bd=2, padx=10, pady=10)
        frame.pack(fill=tk.X, pady=(0, 15))
        frame.config(highlightbackground=self.surface_color, highlightthickness=1)
        
        # Quality
        qual_frame = tk.Frame(frame, bg=self.bg_color)
        qual_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(qual_frame, text="Quality:", bg=self.bg_color,
                fg=self.text_color, font=("Segoe UI", 10)).pack(side=tk.LEFT)
        
        self.quality_var = tk.StringVar(value="best")
        qual_menu = tk.OptionMenu(qual_frame, self.quality_var, "best", "320k", "256k", "192k", "128k")
        qual_menu.config(bg=self.surface_color, fg=self.text_color,
                        font=("Segoe UI", 10), relief=tk.FLAT, highlightthickness=0)
        qual_menu["menu"].config(bg=self.surface_color, fg=self.text_color, relief=tk.FLAT)
        qual_menu.pack(side=tk.LEFT, padx=(10, 30))
        
        # Directory
        dir_frame = tk.Frame(frame, bg=self.bg_color)
        dir_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(dir_frame, text="Save to:", bg=self.bg_color,
                fg=self.text_color, font=("Segoe UI", 10)).pack(side=tk.LEFT)
        
        self.path_label = tk.Label(dir_frame, text=truncate_path(self.download_path),
                                  bg=self.surface_color, fg=self.text_color,
                                  font=("Segoe UI", 9), padx=10, pady=3)
        self.path_label.pack(side=tk.LEFT, padx=(10, 5))
        
        ModernButton(dir_frame, text="Browse", command=self.browse_dir,
                    bg_color="#5a5a5a").pack(side=tk.RIGHT)
        
        # Playlist
        self.playlist_var = tk.BooleanVar(value=False)
        tk.Checkbutton(frame, text="Download entire playlist", variable=self.playlist_var,
                      bg=self.bg_color, fg=self.text_color, selectcolor=self.surface_color,
                      activebackground=self.bg_color, font=("Segoe UI", 10)).pack(anchor=tk.W, pady=(5, 0))
        
    def create_download_button(self, parent):
        self.download_btn = ModernButton(parent, text="⬇️  Download MP3",
                                        command=self.start_download,
                                        bg_color=self.accent_color, font_size=12)
        self.download_btn.pack(pady=15)
        
    def create_progress_section(self, parent):
        frame = tk.LabelFrame(
            parent,
            text=" Progress ",
            bg=self.bg_color,
            fg="#888888",
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            bd=2,
            padx=10,
            pady=10
        )
        frame.pack(fill=tk.X, pady=(0, 15))
        frame.config(highlightbackground=self.surface_color, highlightthickness=1)
        
        # Get frame width for progress bar
        frame.update_idletasks()
        width = frame.winfo_width() - 40  # Account for padding
        if width < 100:
            width = 700  # Default width
            
        self.progress_bar = ProgressBar(frame, width=width, height=25)
        self.progress_bar.pack(fill=tk.X, expand=True, pady=5)
        
        self.status_label = tk.Label(
            frame,
            text="Ready to download",
            bg=self.bg_color,
            fg="#888888",
            font=("Segoe UI", 10)
        )
        self.status_label.pack(pady=(5, 0))
        
    def create_log_section(self, parent):
        frame = tk.LabelFrame(parent, text=" Activity Log ", bg=self.bg_color,
                             fg="#888888", font=("Segoe UI", 10),
                             relief=tk.FLAT, bd=2, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        frame.config(highlightbackground=self.surface_color, highlightthickness=1)
        
        self.log_text = LogText(frame, height=8)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = tk.Frame(frame, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ModernButton(btn_frame, text="Clear Log", command=self.log_text.clear,
                    bg_color="#5a5a5a").pack(side=tk.RIGHT)
        
    def create_footer(self, parent):
        footer = tk.Frame(parent, bg=self.bg_color)
        footer.pack(fill=tk.X)
        
        self.open_btn = ModernButton(footer, text="📁 Open Folder",
                                    command=self.open_folder, bg_color="#5a5a5a")
        self.open_btn.pack(side=tk.LEFT)
        self.open_btn.config(state=tk.DISABLED)
        
        tk.Label(footer, text="Downloads saved as MP3 with metadata",
                bg=self.bg_color, fg="#666666", font=("Segoe UI", 9)).pack(side=tk.RIGHT)
        
    def paste_url(self):
        try:
            clipboard = self.root.clipboard_get()
            self.url_entry.set_value(clipboard)
            self.log(f"📋 Pasted: {clipboard[:50]}...", "info")
        except tk.TclError:
            self.log("❌ Clipboard empty", "error")
            
    def browse_dir(self):
        dir_selected = filedialog.askdirectory(initialdir=self.download_path)
        if dir_selected:
            self.download_path = dir_selected
            self.path_label.config(text=truncate_path(dir_selected))
            self.log(f"📁 Save location: {dir_selected}", "info")
            
    def open_folder(self):
        try:
            os.system(f'xdg-open "{self.download_path}"')
        except:
            self.log("❌ Could not open folder", "error")
            
    def update_status(self, message, percent=None):
        self.status_label.config(text=message)
        if percent is not None:
            self.progress_bar.set_progress(percent)
        self.root.update_idletasks()
            
    def log(self, message, tag=None):
        self.log_text.log(message, tag)
        
    def start_download(self):
        print("Start download clicked")
        if self.is_downloading:
            print("Already downloading, ignoring")
            return
            
        url = self.url_entry.get_value().strip()
        print(f"URL: {url}")
        
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
            
        if "youtube.com" not in url and "youtu.be" not in url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return
            
        self.is_downloading = True
        self.download_btn.config(state=tk.DISABLED)
        self.open_btn.config(state=tk.DISABLED)
        self.log_text.clear()
        self.progress_bar.set_progress(0)
        
        print("Starting download thread...")
        thread = threading.Thread(target=self.download_thread, args=(url,), daemon=True)
        thread.start()
        print("Thread started")
        
    def download_thread(self, url):
        """Background thread for download"""
        print("Download thread running")
        quality = self.quality_var.get()
        
        # Get info
        self.queue_message("status", "Fetching video info...", 5)
        info = self.downloader.extract_info(url)
        
        if info:
            self.queue_message("log", f"📹 {info['title']}", "success")
            self.queue_message("log", f"👤 {info['uploader']}", "success")
            self.queue_message("log", f"⏱️  {format_duration(info['duration'])}", "success")
        
        # Download
        print("Starting actual download...")
        success = self.downloader.download(url, self.download_path, quality, self.playlist_var.get())
        print(f"Download result: {success}")
        
    def download_finished(self, success):
        """Called on main thread when done"""
        print(f"Download finished: {success}")
        self.is_downloading = False
        self.download_btn.config(state=tk.NORMAL)
        
        if success:
            self.open_btn.config(state=tk.NORMAL)
            # Use modern dialog instead of messagebox
            from widgets import ModernSuccessDialog
            ModernSuccessDialog(
                self.root,
                title="Success",
                message="Download completed!",
                details=f"Saved to:\n{self.download_path}"
            )
        else:
            self.progress_bar.set_progress(0)
            self.update_status("Download failed")
            # Show error dialog with details
            messagebox.showerror("Download Failed", 
                "The download failed. Possible reasons:\n\n"
                "1. Video already exists (file overwrite disabled)\n"
                "2. Network connection issue\n"
                "3. YouTube blocking the request\n"
                "4. Video is private or age-restricted\n\n"
                "Check the Activity Log for details.")