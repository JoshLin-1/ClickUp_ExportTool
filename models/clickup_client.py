"""
ClickUp API Client
Handles all API communication with ClickUp
"""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from config.settings import CLICKUP_BASE_URL, REQUEST_TIMEOUT
from .data_models import User, Workspace, Space, Folder, Task, TimeEntry, ApiResponse


class ClickUpClient:
    """ClickUp API client for all API operations"""
    
    def __init__(self, auth_token: str = ""):
        self.auth_token = auth_token
        self.headers = {}
        if auth_token:
            self.headers = {"Authorization": auth_token}
    
    def set_auth_token(self, token: str):
        """Set authentication token"""
        self.auth_token = token
        self.headers = {"Authorization": token}
    
    def _make_request(self, endpoint: str, params: Dict = None) -> ApiResponse:
        """Make API request with error handling"""
        try:
            url = f"{CLICKUP_BASE_URL}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                return ApiResponse(success=True, data=response.json(), status_code=response.status_code)
            else:
                return ApiResponse(
                    success=False, 
                    error=f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
        except Exception as e:
            return ApiResponse(success=False, error=str(e))
    
    def get_workspaces(self) -> List[Workspace]:
        """Get all workspaces/teams"""
        response = self._make_request("team")
        if not response.success:
            raise Exception(response.error)
        
        workspaces = []
        teams = response.data.get('teams', [])
        
        for team in teams:
            # Get members for this team
            members = []
            for member in team.get('members', []):
                user_info = member.get('user', {})
                if user_info.get('id'):
                    user = User(
                        id=user_info['id'],
                        username=user_info.get('username', 'Unknown'),
                        email=user_info.get('email', '')
                    )
                    members.append(user)
            
            workspace = Workspace(
                id=team['id'],
                name=team['name'],
                members=members
            )
            workspaces.append(workspace)
        
        return workspaces
    
    def get_spaces(self, team_id: str) -> List[Space]:
        """Get spaces for a team"""
        response = self._make_request(f"team/{team_id}/space")
        if not response.success:
            raise Exception(response.error)
        
        spaces = []
        for space in response.data.get('spaces', []):
            spaces.append(Space(
                id=space['id'],
                name=space['name'],
                team_id=team_id
            ))
        
        return spaces
    
    def get_folders(self, space_id: str) -> List[Folder]:
        """Get folders in a space"""
        response = self._make_request(f"space/{space_id}/folder")
        if not response.success:
            raise Exception(response.error)
        
        folders = []
        for folder in response.data.get('folders', []):
            folders.append(Folder(
                id=folder['id'],
                name=folder['name']
            ))
        
        return folders
    
    def get_time_entries(self, team_id: str, user_id: str, start_date: datetime, end_date: datetime) -> List[TimeEntry]:
        """Get time entries for a user"""
        start_timestamp = int(start_date.timestamp() * 1000)
        end_timestamp = int((end_date + timedelta(days=1)).timestamp() * 1000)
        
        params = {
            "assignee": user_id,
            "start_date": start_timestamp,
            "end_date": end_timestamp,
            "include_task_tags": "true",
            "include_location_names": "true"
        }
        
        response = self._make_request(f"team/{team_id}/time_entries", params)
        if not response.success:
            raise Exception(response.error)
        
        time_entries = []
        for entry in response.data.get('data', []):
            start_time = datetime.fromtimestamp(int(entry.get('start', 0)) / 1000)
            duration_ms = int(entry.get('duration', 0))
            duration_hours = round(duration_ms / (1000 * 60 * 60), 2)
            
            task_info = entry.get('task', {})
            task_location = entry.get('task_location', {})
            
            time_entry = TimeEntry(
                id=entry.get('id', ''),
                username='',  # Will be set by caller
                email='',     # Will be set by caller
                date=start_time.strftime("%Y-%m-%d"),
                workspace=task_location.get('space_name', 'Unknown'),
                list_name=task_location.get('list_name', 'Unknown'),
                task_name=task_info.get('name', 'No Task'),
                description=entry.get('description', ''),
                hours=duration_hours,
                url=entry.get('task_url', '')
            )
            time_entries.append(time_entry)
        
        return time_entries
    
    def get_tasks_in_folder(self, folder_id: str) -> List[Task]:
        """Get all tasks in a folder"""
        # First get lists in folder
        response = self._make_request(f"folder/{folder_id}/list")
        if not response.success:
            raise Exception(response.error)
        
        all_tasks = []
        lists = response.data.get('lists', [])
        
        for lst in lists:
            list_id = lst['id']
            list_name = lst['name']
            
            # Get tasks in this list
            task_response = self._make_request(f"list/{list_id}/task", {'include_closed': 'true'})
            if task_response.success:
                for task_data in task_response.data.get('tasks', []):
                    task = self._parse_task(task_data, list_name, list_id)
                    all_tasks.append(task)
        
        return all_tasks
    
    def _parse_task(self, task_data: Dict, list_name: str, list_id: str) -> Task:
        """Parse task data from API response"""
        # Parse assignees
        assignees = []
        for assignee in task_data.get('assignees', []):
            assignees.append(assignee.get('username', ''))
        
        # Parse dates
        due_date = None
        if task_data.get('due_date') and task_data.get('due_date') != 'null':
            try:
                due_date = datetime.fromtimestamp(int(task_data['due_date']) / 1000).strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                pass
        
        start_date = None
        if task_data.get('start_date') and task_data.get('start_date') != 'null':
            try:
                start_date = datetime.fromtimestamp(int(task_data['start_date']) / 1000).strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                pass
        
        # Parse custom fields
        custom_fields = {}
        for field in task_data.get('custom_fields', []):
            field_name = field.get('name', '')
            if field_name:
                custom_fields[field_name] = self._extract_custom_field_value(field)
        
        return Task(
            id=task_data.get('id', ''),
            name=task_data.get('name', ''),
            status=task_data.get('status', {}).get('status', ''),
            description=self._clean_text(task_data.get('description', '')),
            list_name=list_name,
            list_id=list_id,
            assignees=assignees,
            due_date=due_date,
            start_date=start_date,
            time_spent=task_data.get('time_spent', 0) or 0,
            time_estimate=task_data.get('time_estimate', 0) or 0,
            points=task_data.get('points', 0) or 0,
            custom_fields=custom_fields,
            url=task_data.get('url', '')
        )
    
    def _extract_custom_field_value(self, field: Dict) -> str:
        """Extract value from custom field"""
        field_type = field.get('type', '')
        value = field.get('value')
        
        if value is None:
            return ''
        
        if field_type == 'drop_down':
            options = field.get('type_config', {}).get('options', [])
            if isinstance(value, (int, str)):
                for option in options:
                    if option.get('orderindex') == value or option.get('id') == value:
                        return option.get('name', str(value))
            return str(value)
        
        elif field_type == 'automatic_progress':
            if isinstance(value, dict):
                return f"{value.get('percent_complete', 0)}%"
            return str(value)
        
        else:
            return str(value)
    
    def _clean_text(self, text: str) -> str:
        """Clean text for Excel compatibility"""
        if not text:
            return ''
        
        import re
        text = re.sub(r'<[^>]+>', '', str(text))
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = ' '.join(text.split())
        
        return text[:32767]  # Excel cell limit