import tkinter as tk
from tkinter import ttk
from typing import List, Callable
from models import Workspace


class WorkspaceSection(ttk.Frame):
    """Workspace selection section"""
    
    def __init__(self, parent, on_select_callback: Callable[[str], None]):
        super().__init__(parent)
        self.on_select_callback = on_select_callback
        self.workspace_combo = None
        self.workspaces: List[Workspace] = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Workspace label
        ttk.Label(self, text="Workspace:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        
        # Workspace combobox
        self.workspace_combo = ttk.Combobox(self, width=50, state="readonly")
        self.workspace_combo.grid(
            row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5
        )
        self.workspace_combo.bind('<<ComboboxSelected>>', self._on_workspace_selected)
        
        # Configure column weights
        self.columnconfigure(1, weight=1)
    
    def set_workspaces(self, workspaces: List[Workspace]):
        """Set available workspaces"""
        self.workspaces = workspaces
        
        # Update combobox values
        values = [ws.display_name for ws in workspaces]
        self.workspace_combo['values'] = values
        
        # Select first workspace if available
        if values:
            self.workspace_combo.set(values[0])
            self._on_workspace_selected(None)
    
    def _on_workspace_selected(self, event):
        """Handle workspace selection"""
        if not self.workspace_combo.get():
            return
        
        # Extract workspace ID from display name
        selected_text = self.workspace_combo.get()
        workspace_id = selected_text.split("ID: ")[1].rstrip(")")
        
        self.on_select_callback(workspace_id)
    
    def get_selected_workspace_id(self) -> str:
        """Get selected workspace ID"""
        if not self.workspace_combo.get():
            return None
        
        selected_text = self.workspace_combo.get()
        return selected_text.split("ID: ")[1].rstrip(")")