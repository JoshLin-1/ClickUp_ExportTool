"""
ClickUp Tools - Main Entry Point
Select and run different ClickUp tools
"""
import tkinter as tk
from tkinter import ttk, messagebox

from views.time_tracker_view import TimeTrackerView
from views.task_reporter_view import TaskReporterView
from controllers.time_tracker_controller import TimeTrackerController
from controllers.task_reporter_controller import TaskReporterController


class ToolSelector:
    """Main application to select which tool to run"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ClickUp Tools - Select Tool")
        self.root.geometry("400x300")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the tool selection UI"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="ClickUp Tools", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Description
        desc_label = ttk.Label(main_frame, text="Select a tool to run:", font=("Arial", 12))
        desc_label.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Tool buttons
        time_tracker_btn = ttk.Button(
            main_frame, 
            text="Time Tracker", 
            command=self.run_time_tracker,
            width=20
        )
        time_tracker_btn.grid(row=2, column=0, pady=10, padx=10)
        
        task_reporter_btn = ttk.Button(
            main_frame, 
            text="Task Reporter", 
            command=self.run_task_reporter,
            width=20
        )
        task_reporter_btn.grid(row=2, column=1, pady=10, padx=10)
        
        # Descriptions
        time_desc = ttk.Label(
            main_frame, 
            text="Export time tracking data\norganized by users",
            justify=tk.CENTER,
            font=("Arial", 9)
        )
        time_desc.grid(row=3, column=0, pady=5, padx=10)
        
        task_desc = ttk.Label(
            main_frame, 
            text="Export task data\norganized by folders",
            justify=tk.CENTER,
            font=("Arial", 9)
        )
        task_desc.grid(row=3, column=1, pady=5, padx=10)
        
        # Exit button
        exit_btn = ttk.Button(main_frame, text="Exit", command=self.root.quit)
        exit_btn.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def run_time_tracker(self):
        """Run the time tracker tool"""
        self.root.withdraw()  # Hide selector window
        
        try:
            tracker_root = tk.Toplevel()
            tracker_view = TimeTrackerView(tracker_root)
            tracker_controller = TimeTrackerController(tracker_view)
            
            # When tracker window closes, show selector again
            def on_tracker_close():
                tracker_root.destroy()
                self.root.deiconify()
            
            tracker_root.protocol("WM_DELETE_WINDOW", on_tracker_close)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start Time Tracker: {str(e)}")
            self.root.deiconify()
    
    def run_task_reporter(self):
        """Run the task reporter tool"""
        self.root.withdraw()  # Hide selector window
        
        try:
            reporter_root = tk.Toplevel()
            reporter_view = TaskReporterView(reporter_root)
            reporter_controller = TaskReporterController(reporter_view)
            
            # When reporter window closes, show selector again
            def on_reporter_close():
                reporter_root.destroy()
                self.root.deiconify()
            
            reporter_root.protocol("WM_DELETE_WINDOW", on_reporter_close)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start Task Reporter: {str(e)}")
            self.root.deiconify()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ToolSelector(root)
    root.mainloop()


if __name__ == "__main__":
    main()