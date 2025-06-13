"""
Task Reporter View
UI for the task reporting tool
"""
import tkinter as tk
from tkinter import ttk

from .base_view import BaseView
from config.settings import MAIN_WINDOW_SIZE


class TaskReporterView(BaseView):
    """Task reporter specific UI components"""
    
    def __init__(self, root):
        super().__init__(root, "ClickUp Task Reporter - Folder-based Excel Reports", MAIN_WINDOW_SIZE)
        
        # Specific UI elements
        self.space_combo = None
        self.folders_tree = None
        self.options = {}
        
        self.setup_specific_ui()
        self.setup_layout()
    
    def setup_specific_ui(self):
        """Setup task reporter specific UI"""
        # 2. Space Selection
        ttk.Label(self.main_frame, text="Space:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.space_var = tk.StringVar()
        self.space_combo = ttk.Combobox(
            self.main_frame, textvariable=self.space_var, 
            width=50, state="readonly"
        )
        self.space_combo.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 3. Folders Display
        ttk.Label(self.main_frame, text="Folders Found:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        
        folders_frame, self.folders_tree = self.create_treeview_with_scrollbar(
            self.main_frame, ('Lists', 'Tasks')
        )
        folders_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure tree columns
        self.folders_tree.heading('#0', text='Folder Name')
        self.folders_tree.heading('Lists', text='Lists Count')
        self.folders_tree.heading('Tasks', text='Tasks Count')
        self.folders_tree.column('#0', width=300)
        self.folders_tree.column('Lists', width=100)
        self.folders_tree.column('Tasks', width=100)
        
        # 4. Options
        options_config = [
            ('custom_fields', 'Include Custom Fields', True),
            ('time_tracking', 'Include Time Tracking Data', True),
            ('assignees', 'Include Assignees', True),
            ('dates', 'Include Due Dates', True)
        ]
        self.create_options_section(4, options_config)
        
        # 5. Action Buttons
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=4, pady=20)
        
        self.fetch_btn = ttk.Button(buttons_frame, text="Fetch All Tasks")
        self.fetch_btn.grid(row=0, column=0, padx=10)
        
        self.export_btn = ttk.Button(buttons_frame, text="Generate Excel Report")
        self.export_btn.grid(row=0, column=1, padx=10)
    
    def setup_layout(self):
        """Setup the layout positioning"""
        # Position common elements
        self.position_progress_bar(6)
        self.position_results_section(7)
        self.position_status_label(9)
        
        # Configure grid weights
        self.main_frame.rowconfigure(3, weight=0)  # Folders tree
        self.main_frame.rowconfigure(8, weight=1)  # Results area
    
    def populate_spaces(self, spaces):
        """Populate space dropdown"""
        space_options = [space.display_name() for space in spaces]
        self.space_combo['values'] = space_options
        if space_options:
            self.space_combo.set(space_options[0])
    
    def get_selected_space_index(self):
        """Get selected space index"""
        return self.space_combo.current()
    
    def populate_folders(self, folders):
        """Populate folders tree"""
        self.folders_tree.delete(*self.folders_tree.get_children())
        for folder in folders:
            self.folders_tree.insert('', 'end', text=folder.name, 
                                   values=(folder.lists_count, folder.tasks_count))
    
    def get_option_values(self):
        """Get all option values"""
        return {key: var.get() for key, var in self.options.items()}