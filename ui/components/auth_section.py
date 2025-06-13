import tkinter as tk
from tkinter import ttk
from typing import Callable


class AuthSection(ttk.Frame):
    """Authentication section for entering ClickUp API token"""
    
    def __init__(self, parent, on_connect_callback: Callable[[str], None]):
        super().__init__(parent)
        self.on_connect_callback = on_connect_callback
        self.token_entry = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Token label
        ttk.Label(self, text="Auth Token:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        
        # Token entry
        self.token_entry = ttk.Entry(self, width=60, show="*")
        self.token_entry.grid(
            row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5
        )
        
        # Connect button
        connect_btn = ttk.Button(
            self, text="Connect",
            command=self._on_connect_clicked
        )
        connect_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Configure column weights
        self.columnconfigure(1, weight=1)
    
    def _on_connect_clicked(self):
        """Handle connect button click"""
        token = self.token_entry.get().strip()
        self.on_connect_callback(token)
    
    def get_token(self) -> str:
        """Get the entered token"""
        return self.token_entry.get().strip()