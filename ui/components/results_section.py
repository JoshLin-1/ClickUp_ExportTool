import tkinter as tk
from tkinter import ttk


class ResultsSection(ttk.Frame):
    """Results display section with text widget"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.results_text = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Results label
        ttk.Label(self, text="Results Summary:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        
        # Text widget frame
        text_frame = ttk.Frame(self)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Results text widget
        self.results_text = tk.Text(text_frame, height=8, width=80)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL,
            command=self.results_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure weights
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
    
    def clear(self):
        """Clear results text"""
        self.results_text.delete(1.0, tk.END)
    
    def add_result(self, text: str):
        """Add a result line"""
        self.results_text.insert(tk.END, text + "\n")
    
    def add_summary(self, *lines: str):
        """Add summary lines"""
        self.results_text.insert(tk.END, "\n--- SUMMARY ---\n")
        for line in lines:
            self.results_text.insert(tk.END, line + "\n")
    
    def get_text(self) -> str:
        """Get all text content"""
        return self.results_text.get(1.0, tk.END)