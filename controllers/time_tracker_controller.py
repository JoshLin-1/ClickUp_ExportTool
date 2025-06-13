"""
Time Tracker Controller
Business logic for time tracking functionality
"""
from tkinter import messagebox
from collections import defaultdict
import os

from .base_controller import BaseController
from utils.excel_exporter import ExcelExporter
from config.settings import MESSAGES


class TimeTrackerController(BaseController):
    """Controller for time tracking functionality"""
    
    def __init__(self, view):
        super().__init__(view)
        self.selected_workspace = None
        self.users = []
        self.time_entries = {}
        
        # Bind specific events
        self.view.workspace_combo.bind('<<ComboboxSelected>>', self.on_workspace_selected)
        self.view.select_all_btn.config(command=self.view.select_all_users)
        self.view.clear_all_btn.config(command=self.view.clear_all_users)
        self.view.fetch_btn.config(command=self.fetch_time_entries)
        self.view.export_btn.config(command=self.export_excel)
    
    def on_connection_success(self):
        """Handle successful connection"""
        self.view.populate_workspaces(self.workspaces)
        if self.workspaces:
            self.on_workspace_selected()  # Auto-load first workspace
    
    def on_workspace_selected(self, event=None):
        """Handle workspace selection"""
        selected_index = self.view.get_selected_workspace_index()
        if selected_index < 0 or selected_index >= len(self.workspaces):
            return
        
        self.selected_workspace = self.workspaces[selected_index]
        self.users = self.selected_workspace.members
        
        self.view.populate_users(self.users)
        self.view.select_all_users()  # Select all users by default
        
        self.view.set_status(f"Loaded {len(self.users)} users")
        self.view.log(f"✓ Loaded {len(self.users)} users from workspace")
    
    def fetch_time_entries(self):
        """Fetch time entries for selected users"""
        if not self.selected_workspace:
            messagebox.showerror("Error", MESSAGES['no_workspace'])
            return
        
        selected_indices = self.view.get_selected_user_indices()
        if not selected_indices:
            messagebox.showerror("Error", MESSAGES['no_users'])
            return
        
        # Validate dates
        date_range = self.validate_date_range()
        if not date_range:
            return
        
        start_date, end_date = date_range
        selected_users = [self.users[i] for i in selected_indices]
        
        self.view.set_status("Fetching time entries...")
        self.view.clear_results()
        self.view.log(f"Fetching time entries for {len(selected_users)} users...")
        
        self.time_entries = {}
        
        try:
            for i, user in enumerate(selected_users):
                self.update_progress(i, len(selected_users), f"Fetching entries for {user.username}...")
                
                try:
                    entries = self.client.get_time_entries(
                        self.selected_workspace.id, user.id, start_date, end_date
                    )
                    
                    # Set user info for each entry
                    for entry in entries:
                        entry.username = user.username
                        entry.email = user.email
                    
                    self.time_entries[user.username] = entries
                    total_hours = sum(entry.hours for entry in entries)
                    self.view.log(f"✓ {user.username}: {len(entries)} entries, {total_hours:.2f} hours")
                    
                except Exception as e:
                    self.view.log(f"✗ {user.username}: Error - {str(e)}")
                    self.time_entries[user.username] = []
            
            # Summary
            total_entries = sum(len(entries) for entries in self.time_entries.values())
            total_hours = sum(
                sum(entry.hours for entry in entries) 
                for entries in self.time_entries.values()
            )
            
            self.view.log(f"\n=== SUMMARY ===")
            self.view.log(f"Users processed: {len(self.time_entries)}")
            self.view.log(f"Total entries: {total_entries}")
            self.view.log(f"Total hours: {total_hours:.2f}")
            
            self.view.set_status(f"Completed! {total_entries} entries fetched")
            
        except Exception as e:
            self.handle_error("fetch time entries", e)
        finally:
            self.reset_progress()
    
    def export_excel(self):
        """Export time entries to Excel"""
        if not self.time_entries:
            messagebox.showerror("Error", MESSAGES['no_data'])
            return
        
        file_path = self.get_export_file_path("Save Time Tracking Excel file")
        if not file_path:
            return
        
        self.view.set_status("Creating Excel file...")
        
        try:
            with ExcelExporter(file_path) as exporter:
                # Create summary sheet
                exporter.create_time_summary_sheet(self.time_entries)
                
                # Create all data sheet
                exporter.create_time_data_sheet(self.time_entries)
                
                # Create individual user sheets
                exporter.create_user_time_sheets(self.time_entries)
            
            # Success message
            num_users = len(self.time_entries)
            total_entries = sum(len(entries) for entries in self.time_entries.values())
            
            stats = {
                "Users": num_users,
                "Total entries": total_entries,
                "Sheets created": "Summary, All Data, Individual user sheets"
            }
            
            self.show_export_success(file_path, stats)
            self.view.set_status(f"Export completed: {os.path.basename(file_path)}")
            self.view.log("✓ Excel file exported successfully!")
            
        except Exception as e:
            self.handle_error("export Excel file", e)