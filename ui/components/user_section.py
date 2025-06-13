import tkinter as tk
from tkinter import ttk
from typing import List
from models import User


class UserSection(ttk.Frame):
    """User selection section with multi-select listbox"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.users_listbox = None
        self.users: List[User] = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Users label
        ttk.Label(self, text="Users in Workspace:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        
        # Users listbox frame
        listbox_frame = ttk.Frame(self)
        listbox_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Users listbox
        self.users_listbox = tk.Listbox(listbox_frame, height=6, selectmode=tk.MULTIPLE)
        self.users_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            listbox_frame, orient=tk.VERTICAL,
            command=self.users_listbox.yview
        )
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.users_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Select buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Button(
            button_frame, text="Select All",
            command=self.select_all_users
        ).grid(row=0, column=0, padx=5)
        
        ttk.Button(
            button_frame, text="Select None",
            command=self.select_no_users
        ).grid(row=0, column=1, padx=5)
        
        # Configure weights
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
    
    def set_users(self, users: List[User]):
        """Set available users"""
        self.users = users
        
        # Clear and repopulate listbox
        self.users_listbox.delete(0, tk.END)
        
        for user in users:
            self.users_listbox.insert(tk.END, user.display_name)
        
        # Select all by default
        self.select_all_users()
    
    def select_all_users(self):
        """Select all users"""
        self.users_listbox.selection_set(0, tk.END)
    
    def select_no_users(self):
        """Deselect all users"""
        self.users_listbox.selection_clear(0, tk.END)
    
    def get_selected_users(self) -> List[User]:
        """Get list of selected users"""
        selected_indices = self.users_listbox.curselection()
        return [self.users[i] for i in selected_indices]