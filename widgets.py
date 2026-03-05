#!/usr/bin/env python3
"""
Custom Tkinter widgets with modern styling
"""
import tkinter as tk

class ModernButton(tk.Button):
    """Styled button with hover effects"""
    def __init__(self, parent, text, command=None, 
                 bg_color="#4a9eff", hover_color="#6bb3ff",
                 text_color="white", font_size=10, **kwargs):
        
        self.bg_color = bg_color
        self.hover_color = hover_color
        
        # Remove font from kwargs if present to avoid conflict
        kwargs.pop('font', None)
        
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=text_color,
            font=("Segoe UI", font_size, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            **kwargs
        )
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def on_enter(self, event):
        self.config(bg=self.hover_color)
        
    def on_leave(self, event):
        self.config(bg=self.bg_color)

class ModernEntry(tk.Entry):
    """Styled entry with placeholder"""
    def __init__(self, parent, placeholder="", width=50, **kwargs):
        self.placeholder = placeholder
        self.placeholder_color = "#888888"
        self.default_color = "#ffffff"
        
        super().__init__(
            parent,
            bg="#3b3b3b",
            fg=self.placeholder_color,
            insertbackground="white",
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            width=width,
            **kwargs
        )
        
        if placeholder:
            self.insert(0, placeholder)
            
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        
    def on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_color)
            
    def on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)
            
    def get_value(self):
        val = self.get()
        return "" if val == self.placeholder else val
        
    def set_value(self, value):
        self.delete(0, tk.END)
        self.insert(0, value)
        self.config(fg=self.default_color)

class LogText(tk.Text):
    """Styled log text widget"""
    def __init__(self, parent, height=10, **kwargs):
        super().__init__(
            parent,
            height=height,
            bg="#1e1e1e",
            fg="#cccccc",
            font=("Consolas", 9),
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=10,
            pady=10,
            state=tk.DISABLED,
            **kwargs
        )
        
        # Configure tags for colors
        self.tag_config("success", foreground="#4caf50")
        self.tag_config("error", foreground="#f44336")
        self.tag_config("warning", foreground="#ff9800")
        self.tag_config("info", foreground="#4a9eff")
        
    def log(self, message, tag=None):
        self.config(state=tk.NORMAL)
        self.insert(tk.END, f"{message}\n", tag)
        self.see(tk.END)
        self.config(state=tk.DISABLED)
        
    def clear(self):
        self.config(state=tk.NORMAL)
        self.delete(1.0, tk.END)
        self.config(state=tk.DISABLED)

class ProgressBar(tk.Canvas):
    """Custom progress bar - FIXED VERSION"""
    def __init__(self, parent, width=400, height=20, **kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg="#3b3b3b",
            highlightthickness=0,
            **kwargs
        )
        
        self.width = width
        self.height = height
        
        # Background (full width) - darker gray
        self.bg_rect = self.create_rectangle(
            0, 0, width, height,
            fill="#2b2b2b", outline=""
        )
        
        # Progress fill (starts at 0)
        self.fill_rect = self.create_rectangle(
            0, 0, 0, height,
            fill="#4a9eff", outline=""
        )
        
        # Text (centered)
        self.text = self.create_text(
            width // 2, height // 2,
            text="0%",
            fill="white",
            font=("Segoe UI", 9, "bold")
        )
        
    def set_progress(self, value):
        """Set progress value (0-100)"""
        value = max(0, min(100, value))
        
        # CRITICAL FIX: Ensure 100% fills completely with no gap
        if value >= 100:
            fill_width = self.width  # Fill entire width
        else:
            fill_width = int((value / 100) * self.width)
            
        # Update fill rectangle coordinates - ensure it fills to the edge
        self.coords(self.fill_rect, 0, 0, fill_width, self.height)
        
        # Update text
        self.itemconfig(self.text, text=f"{value:.0f}%")
        
        # Change color on complete
        if value >= 100:
            self.itemconfig(self.fill_rect, fill="#4caf50")  # Green
        else:
            self.itemconfig(self.fill_rect, fill="#4a9eff")  # Blue
            
        # Force immediate update
        self.update()

class ModernSuccessDialog(tk.Toplevel):
    """Modern success popup dialog - FIXED BUTTON"""
    def __init__(self, parent, title="Success", message="Download completed!", 
                 details="", bg_color="#2b2b2b", accent_color="#4caf50"):
        super().__init__(parent)
        
        self.title(title)
        self.configure(bg=bg_color)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog
        self.update_idletasks()
        width = 450
        height = 350
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Main container
        main_frame = tk.Frame(self, bg=bg_color, padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Success icon (checkmark)
        icon_canvas = tk.Canvas(main_frame, width=70, height=70, bg=bg_color, 
                               highlightthickness=0)
        icon_canvas.pack(pady=(0, 20))
        
        # Draw checkmark circle
        icon_canvas.create_oval(5, 5, 65, 65, fill=accent_color, outline="")
        # Draw checkmark
        icon_canvas.create_line(20, 35, 30, 45, fill="white", width=5, capstyle=tk.ROUND)
        icon_canvas.create_line(30, 45, 50, 25, fill="white", width=5, capstyle=tk.ROUND)
        
        # Title
        title_label = tk.Label(main_frame, text=message, bg=bg_color, 
                              fg="white", font=("Segoe UI", 18, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Details
        if details:
            details_label = tk.Label(main_frame, text=details, bg=bg_color,
                                    fg="#aaaaaa", font=("Segoe UI", 11),
                                    wraplength=380, justify=tk.CENTER)
            details_label.pack(pady=(0, 25))
        
        # OK Button - FIXED: Dark text on light button for visibility
        ok_btn = tk.Button(main_frame, text="OK", command=self.destroy,
                          bg=accent_color, fg="#1e1e2e",  # Dark text on green button
                          font=("Segoe UI", 12, "bold"),
                          relief=tk.FLAT, padx=20, pady=12, cursor="hand2",
                          activebackground="#5dbf6e", activeforeground="#1e1e2e")
        ok_btn.pack(pady=10)
        
        # Hover effect for button
        ok_btn.bind("<Enter>", lambda e: ok_btn.config(bg="#5dbf6e"))
        ok_btn.bind("<Leave>", lambda e: ok_btn.config(bg=accent_color))
        
        # Animation: fade in effect
        self.attributes('-alpha', 0)
        self.fade_in()
        
    def fade_in(self, alpha=0):
        if alpha < 1.0:
            alpha += 0.1
            self.attributes('-alpha', alpha)
            self.after(20, lambda: self.fade_in(alpha))