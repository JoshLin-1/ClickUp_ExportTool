"""
Base View Components
Common UI elements shared across all tools
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from config.settings import PADDING, MESSAGES


class BaseView:
    """Base view with common UI components"""
    
    def __init__(self, root, title: str, size: str):
        self.root = root
        self.root.title(title)
        self.root.geometry(size)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding=PADDING)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # Current row for layout
        self.current_row = 0
        
        # Common UI elements
        self.token_entry = None
        self.progress = None
        self.results_text = None
        self.status_label = None
        
        self.setup_common_ui()
    
    def setup_common_ui(self):
        """Setup common UI elements"""
        # 1. Auth Token
        self.create_auth_section()
        
        # Skip some rows for subclass-specific content
        self.current_row += 5
        
        # Progress bar (will be positioned by subclass)
        self.progress = ttk.Progressbar(self.main_frame, mode='determinate')
        
        # Results text area (will be positioned by subclass)
        self.create_results_section()
        
        # Status label (will be positioned by subclass)
        self.status_label = ttk.Label(self.main_frame, text=MESSAGES['ready'])
    
    def create_auth_section(self):
        """Create authentication section"""
        ttk.Label(self.main_frame, text="ClickUp Auth Token:").grid(
            row=self.current_row, column=0, sticky=tk.W, pady=5
        )
        self.token_entry = ttk.Entry(self.main_frame, width=60, show="*")
        self.token_entry.grid(
            row=self.current_row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5
        )
        self.connect_button = ttk.Button(self.main_frame, text="Connect")
        self.connect_button.grid(row=self.current_row, column=3, padx=5)
        self.current_row += 1
    
    def create_results_section(self):
        """Create results display section"""
        results_frame = ttk.Frame(self.main_frame)
        
        self.results_text = tk.Text(results_frame, height=12, width=90)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        results_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        # Configure grid weights
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        return results_frame
    
    def position_progress_bar(self, row: int):
        """Position progress bar at specified row"""
        self.progress.grid(row=row, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
    
    def position_results_section(self, row: int):
        """Position results section at specified row"""
        ttk.Label(self.main_frame, text="Results:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        results_frame = self.create_results_section()
        results_frame.grid(
            row=row+1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5
        )
        self.main_frame.rowconfigure(row+1, weight=1)
    
    def position_status_label(self, row: int):
        """Position status label at specified row"""
        self.status_label.grid(row=row, column=0, columnspan=4, pady=5)
    
    def create_date_range_section(self, row: int, default_days: int = 7):
        """Create date range input section"""
        ttk.Label(self.main_frame, text="Date Range:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        
        date_frame = ttk.Frame(self.main_frame)
        date_frame.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(date_frame, text="From:").grid(row=0, column=0, padx=5)
        self.start_date = ttk.Entry(date_frame, width=12)
        self.start_date.grid(row=0, column=1, padx=5)
        
        ttk.Label(date_frame, text="To:").grid(row=0, column=2, padx=5)
        self.end_date = ttk.Entry(date_frame, width=12)
        self.end_date.grid(row=0, column=3, padx=5)
        
        # Set default dates
        today = datetime.now()
        start_default = today - timedelta(days=default_days)
        self.start_date.insert(0, start_default.strftime("%Y-%m-%d"))
        self.end_date.insert(0, today.strftime("%Y-%m-%d"))
        
        return date_frame
    
    def create_options_section(self, row: int, options: list):
        """Create options checkboxes section"""
        options_frame = ttk.LabelFrame(self.main_frame, text="Options", padding=PADDING)
        options_frame.grid(row=row, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        self.options = {}
        for i, (key, label, default) in enumerate(options):
            var = tk.BooleanVar(value=default)
            ttk.Checkbutton(options_frame, text=label, variable=var).grid(
                row=i//2, column=i%2, sticky=tk.W, padx=20
            )
            self.options[key] = var
        
        return options_frame
    
    def create_listbox_with_scrollbar(self, parent, height: int = 6):
        """Create listbox with scrollbar"""
        listbox_frame = ttk.Frame(parent)
        
        listbox = tk.Listbox(listbox_frame, height=height, selectmode=tk.MULTIPLE)
        listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        listbox.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        return listbox_frame, listbox
    
    def create_treeview_with_scrollbar(self, parent, columns: list, height: int = 8):
        """Create treeview with scrollbar"""
        tree_frame = ttk.Frame(parent)
        
        tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=height)
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        return tree_frame, tree
    
    def log(self, message: str):
        """Log message to results text"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.results_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.results_text.see(tk.END)
        self.root.update()
    
    def set_status(self, message: str):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update()
    
    def clear_results(self):
        """Clear results text"""
        self.results_text.delete(1.0, tk.END)
    
    def get_auth_token(self) -> str:
        """Get auth token from input"""
        return self.token_entry.get().strip()
    
    def get_date_range(self):
        """Get date range from inputs"""
        start_str = self.start_date.get()
        end_str = self.end_date.get()
        
        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_str, "%Y-%m-%d")
        
        return start_date, end_date
    
    def set_progress(self, value: int, maximum: int = 100):
        """Set progress bar value"""
        self.progress['maximum'] = maximum
        self.progress['value'] = value
        self.root.update()
    
    def reset_progress(self):
        """Reset progress bar"""
        self.progress['value'] = 0
        self.root.update()