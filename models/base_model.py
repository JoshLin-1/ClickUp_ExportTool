"""
Base Model
Common data operations and utilities
"""
from datetime import datetime
from typing import Any, Dict, List


class BaseModel:
    """Base model with common operations"""
    
    @staticmethod
    def format_date(timestamp: int) -> str:
        """Convert timestamp to formatted date string"""
        try:
            return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return ''
    
    @staticmethod
    def format_datetime(timestamp: int) -> str:
        """Convert timestamp to formatted datetime string"""
        try:
            return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            return ''
    
    @staticmethod
    def clean_text(text: str, max_length: int = 32767) -> str:
        """Clean text for Excel compatibility"""
        if not text:
            return ''
        
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', str(text))
        # Replace line breaks with spaces
        text = text.replace('\n', ' ').replace('\r', ' ')
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Limit length for Excel
        return text[:max_length]
    
    @staticmethod
    def safe_get(data: Dict, key: str, default: Any = None) -> Any:
        """Safely get value from dictionary"""
        return data.get(key, default) if isinstance(data, dict) else default
    
    @staticmethod
    def milliseconds_to_hours(milliseconds: int) -> float:
        """Convert milliseconds to hours"""
        if not milliseconds or milliseconds <= 0:
            return 0.0
        return round(milliseconds / (1000 * 60 * 60), 2)