from typing import Dict, List, Any, Tuple
from collections import defaultdict
from datetime import datetime
from models import User, TimeEntry, Workspace
from .clickup_client import ClickUpClient


class TimeEntryManager:
    """Manages time entry fetching and processing"""
    
    def __init__(self, client: ClickUpClient):
        self.client = client
        self.all_user_entries: Dict[str, Dict[str, Any]] = {}
    
    def fetch_entries_for_users(
        self,
        workspace_id: str,
        users: List[User],
        start_date: datetime,
        end_date: datetime,
        progress_callback=None
    ) -> Dict[str, Dict[str, Any]]:
        """Fetch time entries for multiple users"""
        self.all_user_entries = {}
        
        for i, user in enumerate(users):
            try:
                entries = self.client.get_time_entries(
                    workspace_id,
                    user.id,
                    start_date,
                    end_date
                )
                
                self.all_user_entries[user.username] = {
                    'user_info': user,
                    'entries': entries
                }
                
                if progress_callback:
                    progress_callback(i + 1, len(users), user.username, len(entries))
                    
            except Exception as e:
                self.all_user_entries[user.username] = {
                    'user_info': user,
                    'entries': [],
                    'error': str(e)
                }
                
                if progress_callback:
                    progress_callback(i + 1, len(users), user.username, 0, str(e))
        
        return self.all_user_entries
    
    def get_user_summary(self) -> List[Dict[str, Any]]:
        """Get summary data for all users"""
        summary_data = []
        total_hours = 0
        total_entries = 0
        
        for username, data in self.all_user_entries.items():
            entries = data['entries']
            user_hours = sum(entry.duration_hours for entry in entries)
            
            summary_data.append({
                'Person Name': username,
                'Total Entries': len(entries),
                'Total Hours': user_hours,
                'Email': data['user_info'].email
            })
            
            total_hours += user_hours
            total_entries += len(entries)
        
        # Add totals row
        summary_data.append({
            'Person Name': 'TOTAL',
            'Total Entries': total_entries,
            'Total Hours': round(total_hours, 2),
            'Email': ''
        })
        
        return summary_data
    
    def create_hierarchical_summary(self) -> List[Dict[str, Any]]:
        """Create a hierarchical summary by workspace -> list -> task -> member"""
        hierarchy = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float))))
        
        # Build hierarchy
        for username, user_data in self.all_user_entries.items():
            entries = user_data['entries']
            
            for entry in entries:
                hierarchy[entry.workspace_name][entry.list_name][entry.task_name][username] += entry.duration_hours
        
        # Convert to summary data
        summary_data = []
        grand_total_hours = 0
        
        for workspace_name in sorted(hierarchy.keys()):
            workspace_total = 0
            
            # Add workspace header
            summary_data.append({
                'Level': 'WORKSPACE',
                'Workspace': workspace_name,
                'List': '',
                'Task': '',
                'Member': '',
                'Hours': '',
                'Entries': ''
            })
            
            for list_name in sorted(hierarchy[workspace_name].keys()):
                list_total = 0
                
                # Add list header
                summary_data.append({
                    'Level': 'LIST',
                    'Workspace': workspace_name,
                    'List': list_name,
                    'Task': '',
                    'Member': '',
                    'Hours': '',
                    'Entries': ''
                })
                
                for task_name in sorted(hierarchy[workspace_name][list_name].keys()):
                    task_total = 0
                    task_entries = 0
                    
                    # Add task header
                    summary_data.append({
                        'Level': 'TASK',
                        'Workspace': workspace_name,
                        'List': list_name,
                        'Task': task_name,
                        'Member': '',
                        'Hours': '',
                        'Entries': ''
                    })
                    
                    # Add member details
                    for member_name in sorted(hierarchy[workspace_name][list_name][task_name].keys()):
                        member_hours = hierarchy[workspace_name][list_name][task_name][member_name]
                        member_entries = self._count_entries(
                            member_name, workspace_name, list_name, task_name
                        )
                        
                        summary_data.append({
                            'Level': 'MEMBER',
                            'Workspace': workspace_name,
                            'List': list_name,
                            'Task': task_name,
                            'Member': member_name,
                            'Hours': round(member_hours, 2),
                            'Entries': member_entries
                        })
                        
                        task_total += member_hours
                        task_entries += member_entries
                    
                    # Update task total
                    self._update_summary_totals(
                        summary_data, 'TASK', workspace_name, list_name,
                        task_name, task_total, task_entries
                    )
                    
                    list_total += task_total
                
                # Update list total
                self._update_summary_totals(
                    summary_data, 'LIST', workspace_name, list_name,
                    '', list_total
                )
                
                workspace_total += list_total
            
            # Update workspace total
            self._update_summary_totals(
                summary_data, 'WORKSPACE', workspace_name, '', '', workspace_total
            )
            
            grand_total_hours += workspace_total
        
        # Add grand total
        total_entries = sum(len(data['entries']) for data in self.all_user_entries.values())
        summary_data.append({
            'Level': 'GRAND TOTAL',
            'Workspace': '',
            'List': '',
            'Task': '',
            'Member': '',
            'Hours': round(grand_total_hours, 2),
            'Entries': total_entries
        })
        
        return summary_data
    
    def _count_entries(self, member_name: str, workspace: str, list_name: str, task: str) -> int:
        """Count entries for specific member/workspace/list/task combination"""
        if member_name not in self.all_user_entries:
            return 0
        
        count = 0
        for entry in self.all_user_entries[member_name]['entries']:
            if (entry.workspace_name == workspace and
                entry.list_name == list_name and
                entry.task_name == task):
                count += 1
        
        return count
    
    def _update_summary_totals(
        self, summary_data: List[Dict],
        level: str, workspace: str, list_name: str,
        task: str, hours: float, entries: int = None
    ):
        """Update totals in summary data"""
        for row in reversed(summary_data):
            if (row['Level'] == level and
                row['Workspace'] == workspace and
                row['List'] == list_name and
                row['Task'] == task):
                row['Hours'] = round(hours, 2)
                if entries is not None:
                    row['Entries'] = entries
                break