from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class User:
    """Represents a ClickUp user"""
    id: str
    username : str
    email: str = ""

    @classmethod
    def from_api_response(cls, user_data:Dict[str, Any])->'User':
        """Create User instance from ClickUp API response"""
        return cls(
            id = user_data.get('id',''),
            username = user_data.get('username', 'Unknown'),
            email = user_data.get('email', '')
        )
    
    @property
    def display_name(self) -> str: 
        """Get display name for UI"""
        return f"{self.username} ({self.email})" if self.email else self.username
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return{
            'id': self.id, 
            'username':self.username,
            'email': self.email
        }