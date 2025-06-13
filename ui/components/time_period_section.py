import tkinter as tk
from tkinter import ttk
from utils.date_utils import get_default_date_range


class TimePeriodSection(ttk.Frame):
    """Time period selection section"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.start_date_entry = None
        self.end_date_entry = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Time period label
        ttk.Label(self, text="Time Period:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        
        # Date entry frame
        date_frame = ttk.Frame(self)
        date_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Start date
        ttk.Label(date_frame, text="From:").grid(row=0, column=0, padx=5)
        self.start_date_entry = ttk.Entry(date_frame, width=12)
        self.start_date_entry.grid(row=0, column=1, padx=5)
        
        # End date
        ttk.Label(date_frame, text="To:").grid(row=0, column=2, padx=5)
        self.end_date_entry = ttk.Entry(date_frame, width=12)
        self.end_date_entry.grid(row=0, column=3, padx=5)
        
        # Set default dates
        start_date, end_date = get_default_date_range()
        self.start_date_entry.insert(0, start_date)
        self.end_date_entry.insert(0, end_date)
        
        # Configure column weights
        self.columnconfigure(1, weight=1)
    
    def get_start_date(self) -> str:
        """Get start date"""
        return self.start_date_entry.get()
    
    def get_end_date(self) -> str:
        """Get end date"""
        return self.end_date_entry.get()
    
    def set_date_range(self, start_date: str, end_date: str):
        """Set date range"""
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, start_date)
        
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, end_date)