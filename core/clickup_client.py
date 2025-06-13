import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import Workspace, TimeEntry
from config import CLICKUP_API_BASE_URL, DEFAULT_HEADERS


class ClickUpClient:
    """Client for interacting with ClickUp API"""
    
    def __init__(self, auth_token: str = None):
        self.auth_token = auth_token
        self._headers = DEFAULT_HEADERS.copy()
        if auth_token:
            self._headers["Authorization"] = auth_token
    
    def set_auth_token(self, token: str):
        """Set authentication token"""
        self.auth_token = token
        self._headers["Authorization"] = token
    
    def get_workspaces(self) -> List[Workspace]:
        """Fetch all workspaces/teams"""
        if not self.auth_token:
            raise ValueError("Authentication token not set")
        
        response = requests.get(
            f"{CLICKUP_API_BASE_URL}/team",
            headers=self._headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch workspaces: {response.status_code} - {response.text}")
        
        data = response.json()
        workspaces = []
        
        for team_data in data.get('teams', []):
            workspaces.append(Workspace.from_api_response(team_data))
        
        return workspaces
    
    def get_time_entries(
        self,
        workspace_id: str,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[TimeEntry]:
        """Fetch time entries for a specific user"""
        if not self.auth_token:
            raise ValueError("Authentication token not set")
        
        # Convert dates to timestamps
        start_timestamp = int(start_date.timestamp() * 1000)
        end_timestamp = int(end_date.timestamp() * 1000)
        
        params = {
            "assignee": user_id,
            "start_date": start_timestamp,
            "end_date": end_timestamp,
            "include_task_tags": "true",
            "include_location_names": "true",
            "include_approval_history": "false"
        }
        
        response = requests.get(
            f"{CLICKUP_API_BASE_URL}/team/{workspace_id}/time_entries",
            headers=self._headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch time entries: {response.status_code} - {response.text}")
        
        data = response.json()
        entries = []
        
        for entry_data in data.get('data', []):
            entries.append(TimeEntry.from_api_response(entry_data))
        
        return entries
    
    def test_connection(self) -> bool:
        """Test if the connection to ClickUp is valid"""
        try:
            self.get_workspaces()
            return True
        except:
            return False