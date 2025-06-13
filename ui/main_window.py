import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
from typing import List

from config import WINDOW_TITLE, WINDOW_GEOMETRY
from core.clickup_client import ClickUpClient
from core.time_entry_manager import TimeEntryManager
from core.excel_exporter import ExcelExporter
from models import Workspace, User
from utils.date_utils import parse_date_string, add_day_to_timestamp

from .components import (
    AuthSection, WorkspaceSection, UserSection,
    TimePeriodSection, ResultsSection
)


class MainWindow:
    """Main application window"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_GEOMETRY)
        
        # Core components
        self.client = ClickUpClient()
        self.time_manager = TimeEntryManager(self.client)
        
        # Data
        self.workspaces: List[Workspace] = []
        self.selected_workspace: Workspace = None
        
        # UI Components
        self.auth_section = None
        self.workspace_section = None
        self.user_section = None
        self.time_period_section = None
        self.results_section = None
        self.progress_bar = None
        self.status_label = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Auth section
        self.auth_section = AuthSection(main_frame, self.on_connect)
        self.auth_section.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E))
        
        # Workspace section
        self.workspace_section = WorkspaceSection(main_frame, self.on_workspace_selected)
        self.workspace_section.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E))
        
        # Users section
        self.user_section = UserSection(main_frame)
        self.user_section.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Time period section
        self.time_period_section = TimePeriodSection(main_frame)
        self.time_period_section.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E))
        
        # Fetch button
        fetch_btn = ttk.Button(
            main_frame,
            text="Fetch All Users' Time Entries",
            command=self.fetch_time_entries
        )
        fetch_btn.grid(row=4, column=1, pady=20)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # Results section
        self.results_section = ResultsSection(main_frame)
        self.results_section.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Export button
        export_btn = ttk.Button(
            main_frame,
            text="Export to Excel (Multi-Tab)",
            command=self.export_to_excel
        )
        export_btn.grid(row=7, column=1, pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=8, column=0, columnspan=4, pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
    
    def update_status(self, message: str):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update()
    
    def on_connect(self, auth_token: str):
        """Handle connection to ClickUp"""
        if not auth_token:
            messagebox.showerror("Error", "Please enter your auth token")
            return
        
        self.update_status("Connecting to ClickUp...")
        
        try:
            self.client.set_auth_token(auth_token)
            self.workspaces = self.client.get_workspaces()
            
            # Update workspace dropdown
            self.workspace_section.set_workspaces(self.workspaces)
            
            self.update_status("Connected successfully!")
            messagebox.showinfo("Success", "Connected to ClickUp successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
            self.update_status("Connection failed")
    
    def on_workspace_selected(self, workspace_id: str):
        """Handle workspace selection"""
        # Find selected workspace
        self.selected_workspace = None
        for workspace in self.workspaces:
            if workspace.id == workspace_id:
                self.selected_workspace = workspace
                break
        
        if self.selected_workspace:
            self.user_section.set_users(self.selected_workspace.members)
            self.update_status(f"Loaded {len(self.selected_workspace.members)} users")
    
    def fetch_time_entries(self):
        """Fetch time entries for selected users"""
        if not self.client.auth_token:
            messagebox.showerror("Error", "Please connect to ClickUp first")
            return
        
        if not self.selected_workspace:
            messagebox.showerror("Error", "Please select a workspace")
            return
        
        selected_users = self.user_section.get_selected_users()
        if not selected_users:
            messagebox.showerror("Error", "Please select at least one user")
            return
        
        # Get date range
        try:
            start_date = parse_date_string(self.time_period_section.get_start_date())
            end_date = add_day_to_timestamp(
                parse_date_string(self.time_period_section.get_end_date())
            )
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dates in YYYY-MM-DD format")
            return
        
        # Setup progress
        self.progress_bar['maximum'] = len(selected_users)
        self.progress_bar['value'] = 0
        self.results_section.clear()
        
        # Fetch entries
        def progress_callback(current, total, username, entries_count, error=None):
            self.progress_bar['value'] = current
            
            if error:
                self.results_section.add_result(f"{username}: Error - {error}")
            else:
                total_hours = sum(
                    entry.duration_hours 
                    for entry in self.time_manager.all_user_entries[username]['entries']
                )
                self.results_section.add_result(
                    f"{username}: {entries_count} entries, {total_hours} hours"
                )
            
            self.root.update()
        
        self.update_status("Fetching time entries...")
        
        all_entries = self.time_manager.fetch_entries_for_users(
            self.selected_workspace.id,
            selected_users,
            start_date,
            end_date,
            progress_callback
        )
        
        # Show summary
        total_entries = sum(
            len(data['entries']) for data in all_entries.values()
        )
        self.results_section.add_summary(
            f"Total users processed: {len(all_entries)}",
            f"Total time entries: {total_entries}"
        )
        
        self.update_status(
            f"Completed! Fetched {total_entries} entries from {len(all_entries)} users"
        )
    
    def export_to_excel(self):
        """Export data to Excel"""
        if not self.time_manager.all_user_entries:
            messagebox.showerror("Error", "No data to export. Please fetch time entries first.")
            return
        
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            title="Save Excel file",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        self.update_status("Creating Excel file...")
        
        # Setup progress
        total_steps = len(self.time_manager.all_user_entries) + 2
        self.progress_bar['maximum'] = total_steps
        self.progress_bar['value'] = 0
        
        def progress_callback(step):
            self.progress_bar['value'] = step
            self.root.update()
        
        try:
            # Get data
            hierarchical_summary = self.time_manager.create_hierarchical_summary()
            user_summary = self.time_manager.get_user_summary()
            
            # Export
            exporter = ExcelExporter(file_path)
            exporter.export(
                hierarchical_summary,
                user_summary,
                self.time_manager.all_user_entries,
                progress_callback
            )
            
            # Show success message
            num_users = len(self.time_manager.all_user_entries)
            messagebox.showinfo(
                "Export Complete",
                f"Successfully exported data to Excel file:\n{file_path}\n\n"
                f"File contains:\n"
                f"- Hierarchical Summary (Workspace → List → Task → Member)\n"
                f"- User Summary\n"
                f"- {num_users} individual user tabs"
            )
            
            self.update_status(f"Excel export completed! File saved to {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Error creating Excel file: {str(e)}")
            self.update_status("Excel export failed")