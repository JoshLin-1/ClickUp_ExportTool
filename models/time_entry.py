from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass
class TimeEntry:
    """Represents a time entry in CLickUp"""
    id: str 
    start: datetime
    duration_ms: int
    task_name: str
    task_url: str
    description: str
    delivery_name: str
    workpackage_name: str

    @classmethod
    def from_api_response(cls, entry_data: Dict[str, Any]) -> 'TimeEntry':
        """Create TimeEntry instance from ClickUp ApI response"""
        task_location = entry_data.get('task_location', {})
        task_data = entry_data.get('task', {})
        return cls(
            id = entry_data.get('id', ''),
            start= datetime.fromtimestamp(int(entry_data.get('start',0))/1000),
            duration_ms = int(entry_data.get('duration', 0)),
            task_name=task_data.get('name', 'No Task'),
            task_url=entry_data.get('task_url', ''),
            description=entry_data.get('description', ''),
            delivery_name=task_location.get('space_name', 'Unknown Workspace'),
            workpackage_name=task_location.get('list_name', 'Unknown List')
        )
    
    @property
    def duration_hours(self) -> float:
        """Get duration in hours"""
        return round(self.duration_ms/ (1000*60*60),2)
    
    @property
    def date_str(self) -> str:
        """Get formatted date string"""
        return self.start.strftime("%Y-%m-%d")
    
    def to_excel_row(self, username:str)-> Dict[str, Any]:
        """Convert to Excel row format"""
        from config import EXCEL_HEADERS
        return{
            EXCEL_HEADERS['date']:self.date_str,
            EXCEL_HEADERS['employee']:username,
            EXCEL_HEADERS['delivery']:self.delivery_name, 
            EXCEL_HEADERS['workpackage']:self.workpackage_name,
            EXCEL_HEADERS['task']:self.task_name,
            EXCEL_HEADERS['description']:self.description,
            EXCEL_HEADERS['hours']:self.duration_hours,
            EXCEL_HEADERS['url']:self.task_url
        }