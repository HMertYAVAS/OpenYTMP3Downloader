#!/usr/bin/env python3
"""
YouTube download functionality using yt-dlp
"""
import subprocess
import json
import re
import os

class YouTubeDownloader:
    def __init__(self, ui_callback=None):
        self.ui_callback = ui_callback
        self.is_running = False
        self.current_process = None
        
    def safe_callback(self, event_type, message, data=None):
        if self.ui_callback:
            try:
                self.ui_callback(event_type, message, data)
            except Exception as e:
                print(f"Callback error: {e}")
                
    def extract_info(self, url):
        """Get video information"""
        try:
            cmd = ["yt-dlp", "--force-ipv4", "--dump-json", "--no-download", "--no-check-certificate", url]
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout:
                line = result.stdout.strip().split('\n')[0]
                data = json.loads(line)
                return {
                    'title': data.get('title', 'Unknown'),
                    'uploader': data.get('uploader', 'Unknown'),
                    'duration': data.get('duration', 0),
                }
        except Exception as e:
            print(f"Info extraction error: {e}")
        return None
            
    def download(self, url, output_path, quality="best", playlist=False):
        """Download audio"""
        self.is_running = True
        
        try:
            quality_map = {"best": "0", "320k": "320", "256k": "256", "192k": "192", "128k": "128"}
            audio_quality = quality_map.get(quality, "0")
            
            cmd = [
                "yt-dlp",
                "--force-ipv4",
                "--no-warnings",
                "--no-check-certificate",
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", audio_quality,
                "--embed-thumbnail",
                "--add-metadata",
                "--ignore-errors",
                "--geo-bypass",
                "--force-overwrites",  # OVERWRITE EXISTING FILES
                "-f", "bestaudio[ext=m4a]/bestaudio/best",
                "-o", f"{output_path}/%(title)s.%(ext)s",
                "--newline",
                "--progress"
            ]
            
            if not playlist:
                cmd.append("--no-playlist")
            else:
                cmd.append("--yes-playlist")
                
            cmd.append(url)
            
            print(f"Download command: {' '.join(cmd)}")
            self.safe_callback("log", f"Starting download...", "info")
            self.safe_callback("status", "Connecting to YouTube...", 5)
            
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            last_percent = 0
            error_output = []
            
            for line in self.current_process.stdout:
                line = line.strip()
                if not line:
                    continue
                    
                print(f"yt-dlp: {line}")
                
                # Check for errors
                if "ERROR" in line or "error" in line.lower():
                    error_output.append(line)
                    self.safe_callback("log", line, "error")
                    continue
                
                if "[download]" in line:
                    try:
                        match = re.search(r"(\d+\.?\d*)%", line)
                        if match:
                            percent = float(match.group(1))
                            if percent != last_percent:
                                last_percent = percent
                                self.safe_callback("status", f"Downloading... {percent:.1f}%", percent)
                    except:
                        pass
                        
                    if "Destination:" in line:
                        self.safe_callback("log", f"Saving: {line.split('Destination:')[-1].strip()}", "info")
                        
                elif "ExtractAudio" in line or "Converting" in line:
                    self.safe_callback("status", "Converting to MP3...", 90)
                    self.safe_callback("log", "Converting to MP3...", "info")
                    
                elif "Deleting" in line:
                    self.safe_callback("log", "Cleaning up...", "info")
                    
            self.current_process.wait()
            success = self.current_process.returncode == 0
            
            # Check for specific errors
            if not success and error_output:
                error_msg = "\n".join(error_output[-3:])  # Last 3 error lines
                self.safe_callback("log", f"Error details: {error_msg}", "error")
            
            if success:
                self.safe_callback("status", "Complete!", 100)
                self.safe_callback("log", "✅ Download completed!", "success")
            else:
                self.safe_callback("status", "Failed", 0)
                # Provide helpful error message
                if any("already been downloaded" in e for e in error_output):
                    self.safe_callback("log", "⚠️ File already exists (use --force-overwrites)", "warning")
                else:
                    self.safe_callback("log", "❌ Download failed", "error")
                
            self.safe_callback("done", success, None)
            return success
            
        except Exception as e:
            print(f"Download exception: {e}")
            self.safe_callback("log", f"Error: {str(e)}", "error")
            self.safe_callback("status", f"Error", 0)
            self.safe_callback("done", False, None)
            return False
            
        finally:
            self.is_running = False
            self.current_process = None