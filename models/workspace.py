from dataclasses import dataclass
from typing import List, Dict, Any
from .user import User

@dataclass
class Workspace:
    """Represents a ClickUp workspace/team"""
    id: str
    name: str
    members: List[User] = None

    def __post_init__(self):
        if self.members is None:
            self.members = []

    @classmethod
    def from_api_response (cls, workspace_data: Dict[str, any]) -> 'Workspace':
        """Workspace from API response"""
        workspace = cls(
            id = str (workspace_data.get('id', '')),
            name = workspace_data.get('name', 'Unknown')
        )

        #Parse members
        members_data = workspace_data.get('members',[])
        for member_data in members_data:
            user_info = member_data.get('user',{})
            if user_info.get('id'):
                workspace.members.append(User.from_api_response(user_info))
        return workspace
    
    @property
    def display_name(self) -> str:
        """Get displane name for UI"""
        return f"{self.name} (ID:{self.id})"
    
    def get_member_by_username(self, username: str) -> User:
        """Get member by username"""
        for member in self.members:
            if member.username == username:
                return member
            return None
