"""
Data models for ClickUp Tools
Simple data classes to represent ClickUp entities
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class User:
    """Represents a ClickUp user"""
    id: str
    username: str
    email: str = ""
    
    def display_name(self) -> str:
        """Return formatted display name"""
        if self.email:
            return f"{self.username} ({self.email})"
        return self.username


@dataclass
class Workspace:
    """Represents a ClickUp workspace/team"""
    id: str
    name: str
    members: List[User]
    
    def display_name(self) -> str:
        """Return formatted display name"""
        return f"{self.name} (ID: {self.id})"


@dataclass
class Space:
    """Represents a ClickUp space"""
    id: str
    name: str
    team_id: str
    
    def display_name(self) -> str:
        """Return formatted display name"""
        return f"{self.name} (ID: {self.id})"


@dataclass
class Folder:
    """Represents a ClickUp folder"""
    id: str
    name: str
    lists_count: int = 0
    tasks_count: int = 0


@dataclass
class Task:
    """Represents a ClickUp task"""
    id: str
    name: str
    status: str
    description: str = ""
    list_name: str = ""
    list_id: str = ""
    folder_name: str = ""
    folder_id: str = ""
    assignees: List[str] = None
    due_date: Optional[str] = None
    start_date: Optional[str] = None
    time_spent: int = 0  # milliseconds
    time_estimate: int = 0  # milliseconds
    points: int = 0
    custom_fields: Dict[str, Any] = None
    url: str = ""
    
    def __post_init__(self):
        if self.assignees is None:
            self.assignees = []
        if self.custom_fields is None:
            self.custom_fields = {}
    
    @property
    def hours_spent(self) -> float:
        """Convert time_spent from milliseconds to hours"""
        return round(self.time_spent / (1000 * 60 * 60), 2) if self.time_spent > 0 else 0
    
    @property
    def hours_estimated(self) -> float:
        """Convert time_estimate from milliseconds to hours"""
        return round(self.time_estimate / (1000 * 60 * 60), 2) if self.time_estimate > 0 else 0


@dataclass
class TimeEntry:
    """Represents a ClickUp time entry"""
    id: str
    username: str
    email: str
    date: str
    workspace: str
    list_name: str
    task_name: str
    description: str
    hours: float
    url: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Excel export"""
        return {
            '日期': self.date,
            '員工': self.username,
            '信箱': self.email,
            '專案': self.workspace,
            '專項': self.list_name,
            '任務': self.task_name,
            '描述': self.description,
            '工時': self.hours,
            '連結': self.url
        }


@dataclass
class ApiResponse:
    """Represents API response with status and data"""
    success: bool
    data: Any = None
    error: str = ""
    status_code: int = 0