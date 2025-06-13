"""
Time Tracker View
UI for the time tracking tool
"""
import tkinter as tk
from tkinter import ttk

from .base_view import BaseView
from config.settings import SMALL_WINDOW_SIZE


class TimeTrackerView(BaseView):
    """Time tracker specific UI components"""
    
    def __init__(self, root):
        super().__init__(root, "ClickUp Time Tracker - Simple & Reliable", SMALL_WINDOW_SIZE)
        
        # Specific UI elements
        self.workspace_combo = None
        self.users_listbox = None
        self.start_date = None
        self.end_date = None
        
        self.setup_specific_ui()
        self.setup_layout()
    
    def setup_specific_ui(self):
        """Setup time tracker specific UI"""
        # 2. Workspace Selection
        ttk.Label(self.main_frame, text="Workspace:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.workspace_var = tk.StringVar()
        self.workspace_combo = ttk.Combobox(
            self.main_frame, textvariable=self.workspace_var, 
            width=50, state="readonly"
        )
        self.workspace_combo.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 3. Users List
        ttk.Label(self.main_frame, text="Users:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        
        users_frame, self.users_listbox = self.create_listbox_with_scrollbar(self.main_frame)
        users_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Select buttons
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=5)
        self.select_all_btn = ttk.Button(btn_frame, text="Select All")
        self.select_all_btn.grid(row=0, column=0, padx=5)
        self.clear_all_btn = ttk.Button(btn_frame, text="Clear All")
        self.clear_all_btn.grid(row=0, column=1, padx=5)
        
        # 4. Date Range
        self.create_date_range_section(5)
        
        # 5. Action Buttons
        self.fetch_btn = ttk.Button(self.main_frame, text="Fetch Time Entries")
        self.fetch_btn.grid(row=6, column=1, pady=20)
        
        self.export_btn = ttk.Button(self.main_frame, text="Export to Excel")
        self.export_btn.grid(row=8, column=1, pady=10)
    
    def setup_layout(self):
        """Setup the layout positioning"""
        # Position common elements
        self.position_progress_bar(7)
        self.position_results_section(9)
        self.position_status_label(11)
        
        # Configure grid weights
        self.main_frame.rowconfigure(3, weight=0)  # Users list
        self.main_frame.rowconfigure(10, weight=1)  # Results area
    
    def populate_workspaces(self, workspaces):
        """Populate workspace dropdown"""
        workspace_options = [ws.display_name() for ws in workspaces]
        self.workspace_combo['values'] = workspace_options
        if workspace_options:
            self.workspace_combo.set(workspace_options[0])
    
    def populate_users(self, users):
        """Populate users listbox"""
        self.users_listbox.delete(0, tk.END)
        for user in users:
            self.users_listbox.insert(tk.END, user.display_name())
    
    def get_selected_workspace_index(self):
        """Get selected workspace index"""
        return self.workspace_combo.current()
    
    def get_selected_user_indices(self):
        """Get selected user indices"""
        return self.users_listbox.curselection()
    
    def select_all_users(self):
        """Select all users"""
        self.users_listbox.selection_set(0, tk.END)
    
    def clear_all_users(self):
        """Clear all user selections"""
        self.users_listbox.selection_clear(0, tk.END)