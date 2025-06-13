"""
Base Controller
Common functionality shared across all controllers
"""
from tkinter import messagebox, filedialog
from datetime import datetime
from typing import List, Optional

from models.clickup_client import ClickUpClient
from models.data_models import Workspace, Space
from utils.excel_exporter import ExcelExporter
from config.settings import MESSAGES


class BaseController:
    """Base controller with common functionality"""
    
    def __init__(self, view):
        self.view = view
        self.client = ClickUpClient()
        self.workspaces = []
        self.spaces = []
        
        # Bind common events
        self.view.connect_button.config(command=self.connect)
    
    def connect(self):
        """Connect to ClickUp"""
        auth_token = self.view.get_auth_token()
        if not auth_token:
            messagebox.showerror("Error", MESSAGES['no_token'])
            return
        
        self.view.set_status(MESSAGES['connecting'])
        self.view.log("Connecting to ClickUp...")
        
        try:
            self.client.set_auth_token(auth_token)
            self.workspaces = self.client.get_workspaces()
            
            if self.workspaces:
                self.on_connection_success()
                self.view.set_status(MESSAGES['connected'])
                self.view.log(f"✓ Connected! Found {len(self.workspaces)} workspaces")
            else:
                raise Exception("No workspaces found")
                
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.view.set_status(MESSAGES['connection_failed'])
            self.view.log(f"✗ Connection failed: {e}")
    
    def on_connection_success(self):
        """Override in subclasses to handle successful connection"""
        pass
    
    def get_spaces_for_team(self, team_id: str) -> List[Space]:
        """Get spaces for a team"""
        try:
            return self.client.get_spaces(team_id)
        except Exception as e:
            self.view.log(f"✗ Failed to get spaces: {e}")
            return []
    
    def validate_date_range(self) -> Optional[tuple]:
        """Validate and return date range"""
        try:
            return self.view.get_date_range()
        except ValueError:
            messagebox.showerror("Error", MESSAGES['invalid_date'])
            return None
    
    def get_export_file_path(self, title: str = "Save Excel file") -> Optional[str]:
        """Get file path for export"""
        return filedialog.asksaveasfilename(
            title=title,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
    
    def show_export_success(self, file_path: str, stats: dict):
        """Show export success message"""
        stats_text = "\n".join([f"{key}: {value}" for key, value in stats.items()])
        
        messagebox.showinfo(
            "Export Complete",
            f"Excel file created successfully!\n\n"
            f"Location: {file_path}\n\n"
            f"{stats_text}"
        )
    
    def handle_error(self, operation: str, error: Exception):
        """Handle and display errors"""
        error_msg = f"Failed to {operation}: {str(error)}"
        messagebox.showerror("Error", error_msg)
        self.view.log(f"✗ {error_msg}")
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """Update progress bar and status"""
        self.view.set_progress(current, total)
        if message:
            self.view.set_status(message)
    
    def reset_progress(self):
        """Reset progress bar"""
        self.view.reset_progress()