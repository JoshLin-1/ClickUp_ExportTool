"""
Task Reporter Controller
Business logic for task reporting functionality
"""
from tkinter import messagebox
from collections import defaultdict
import os

from .base_controller import BaseController
from utils.excel_exporter import ExcelExporter
from config.settings import MESSAGES


class TaskReporterController(BaseController):
    """Controller for task reporting functionality"""
    
    def __init__(self, view):
        super().__init__(view)
        self.selected_space = None
        self.folders = []
        self.tasks_by_folder = {}
        
        # Bind specific events
        self.view.space_combo.bind('<<ComboboxSelected>>', self.on_space_selected)
        self.view.fetch_btn.config(command=self.fetch_all_tasks)
        self.view.export_btn.config(command=self.generate_excel_report)
    
    def on_connection_success(self):
        """Handle successful connection"""
        # Get all spaces from all teams
        all_spaces = []
        for workspace in self.workspaces:
            try:
                spaces = self.get_spaces_for_team(workspace.id)
                all_spaces.extend(spaces)
            except Exception as e:
                self.view.log(f"Warning: Could not get spaces for {workspace.name}: {e}")
        
        self.spaces = all_spaces
        self.view.populate_spaces(self.spaces)
        
        if self.spaces:
            self.on_space_selected()  # Auto-load first space
    
    def on_space_selected(self, event=None):
        """Handle space selection"""
        selected_index = self.view.get_selected_space_index()
        if selected_index < 0 or selected_index >= len(self.spaces):
            return
        
        self.selected_space = self.spaces[selected_index]
        self.load_folders()
    
    def load_folders(self):
        """Load folders for selected space"""
        if not self.selected_space:
            return
        
        self.view.set_status("Loading folders...")
        self.view.log(f"Loading folders for space {self.selected_space.name}...")
        
        try:
            self.folders = self.client.get_folders(self.selected_space.id)
            
            # Count lists and tasks for each folder (simplified)
            self.update_progress(0, len(self.folders), "Counting tasks in folders...")
            
            for i, folder in enumerate(self.folders):
                self.update_progress(i, len(self.folders), f"Loading folder: {folder.name}")
                
                try:
                    # Get basic count of tasks (simplified to avoid too many API calls)
                    tasks = self.client.get_tasks_in_folder(folder.id)
                    
                    # Count lists
                    lists = set(task.list_name for task in tasks)
                    folder.lists_count = len(lists)
                    folder.tasks_count = len(tasks)
                    
                except Exception as e:
                    self.view.log(f"Warning: Could not count tasks for folder {folder.name}: {e}")
                    folder.lists_count = 0
                    folder.tasks_count = 0
            
            self.view.populate_folders(self.folders)
            self.view.set_status(f"Loaded {len(self.folders)} folders")
            self.view.log("✓ Folders loaded successfully")
            
        except Exception as e:
            self.handle_error("load folders", e)
        finally:
            self.reset_progress()
    
    def fetch_all_tasks(self):
        """Fetch all tasks from all folders"""
        if not self.selected_space:
            messagebox.showerror("Error", MESSAGES['no_space'])
            return
        
        if not self.folders:
            messagebox.showerror("Error", "No folders found. Please load folders first")
            return
        
        self.view.set_status("Fetching all tasks...")
        self.view.clear_results()
        self.view.log("Starting to fetch all tasks...")
        
        self.tasks_by_folder = {}
        total_tasks = 0
        
        try:
            for i, folder in enumerate(self.folders):
                self.update_progress(i, len(self.folders), f"Fetching tasks from folder: {folder.name}")
                self.view.log(f"Processing folder: {folder.name}")
                
                try:
                    tasks = self.client.get_tasks_in_folder(folder.id)
                    
                    # Set folder info for each task
                    for task in tasks:
                        task.folder_name = folder.name
                        task.folder_id = folder.id
                    
                    self.tasks_by_folder[folder.name] = tasks
                    total_tasks += len(tasks)
                    self.view.log(f"  ✓ {folder.name}: {len(tasks)} tasks")
                    
                except Exception as e:
                    self.view.log(f"  ✗ {folder.name}: Error - {str(e)}")
                    self.tasks_by_folder[folder.name] = []
            
            self.view.set_status(f"Completed! Fetched {total_tasks} tasks from {len(self.folders)} folders")
            self.view.log(f"✓ Successfully fetched {total_tasks} total tasks")
            
        except Exception as e:
            self.handle_error("fetch tasks", e)
        finally:
            self.reset_progress()
    
    def generate_excel_report(self):
        """Generate Excel report organized by folders"""
        if not self.tasks_by_folder:
            messagebox.showerror("Error", "No task data available. Please fetch tasks first.")
            return
        
        file_path = self.get_export_file_path("Save Task Report")
        if not file_path:
            return
        
        self.view.set_status("Generating Excel report...")
        self.view.log("Creating Excel report...")
        
        try:
            options = self.view.get_option_values()
            
            with ExcelExporter(file_path) as exporter:
                # Create summary sheet
                exporter.create_task_summary_sheet(self.tasks_by_folder)
                
                # Create individual folder sheets
                for folder_name, tasks in self.tasks_by_folder.items():
                    if tasks:  # Only create sheet if there are tasks
                        exporter.create_folder_task_sheet(
                            folder_name, tasks,
                            include_custom_fields=options.get('custom_fields', True),
                            include_time_tracking=options.get('time_tracking', True),
                            include_assignees=options.get('assignees', True),
                            include_dates=options.get('dates', True)
                        )
                
                # Create time tracking summary if enabled
                if options.get('time_tracking', True):
                    # Flatten all tasks for time tracking summary
                    all_tasks_with_time = []
                    for tasks in self.tasks_by_folder.values():
                        for task in tasks:
                            if task.time_spent > 0 or task.time_estimate > 0 or task.points > 0:
                                all_tasks_with_time.append(task)
                    
                    if all_tasks_with_time:
                        self.create_time_tracking_summary_sheet(exporter, all_tasks_with_time)
            
            # Success message
            total_folders = len([tasks for tasks in self.tasks_by_folder.values() if tasks])
            total_tasks = sum(len(tasks) for tasks in self.tasks_by_folder.values())
            
            stats = {
                "Folders": total_folders,
                "Total tasks": total_tasks,
                "Sheets created": "Summary, Individual folder sheets, Time tracking summary"
            }
            
            self.show_export_success(file_path, stats)
            self.view.set_status(f"Report generated: {os.path.basename(file_path)}")
            self.view.log("✓ Excel report generated successfully!")
            
        except Exception as e:
            self.handle_error("generate report", e)
    
    def create_time_tracking_summary_sheet(self, exporter, tasks):
        """Create time tracking summary sheet for tasks"""
        time_data = []
        
        for task in tasks:
            time_data.append({
                'Folder': task.folder_name,
                'List': task.list_name,
                'Task': task.name,
                'Assignees': ', '.join(task.assignees),
                'Status': task.status,
                'Hours Spent': task.hours_spent,
                'Hours Estimated': task.hours_estimated,
                'Sprint Points': task.points,
                'Task URL': task.url
            })
        
        if time_data:
            import pandas as pd
            df = pd.DataFrame(time_data)
            df = df.sort_values(['Folder', 'Hours Spent'], ascending=[True, False])
            df.to_excel(exporter.writer, sheet_name='Time Tracking', index=False)
            
            exporter._format_header(exporter.writer, 'Time Tracking')
            exporter._auto_adjust_columns('Time Tracking')
            exporter._make_urls_clickable('Time Tracking', 'Task URL')