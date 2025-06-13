# Configuration settings for ClickUp Tools

# API Configuration
CLICKUP_BASE_URL = "https://api.clickup.com/api/v2"
REQUEST_TIMEOUT = 30

# UI Configuration
MAIN_WINDOW_SIZE = "900x800"
SMALL_WINDOW_SIZE = "800x700"
PADDING = "10"

# Date Configuration
DEFAULT_DATE_RANGE_DAYS = 7
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Excel Configuration
MAX_SHEET_NAME_LENGTH = 31
MAX_CELL_LENGTH = 32767
MAX_COLUMN_WIDTH = 50
MIN_COLUMN_WIDTH = 8

# Colors for Excel formatting
COLORS = {
    'header': "366092",
    'header_text': "FFFFFF",
    'list_header': "70AD47",
    'list_header_text': "FFFFFF",
    'task_header': "4472C4",
    'task_header_text': "FFFFFF",
    'link': "0000FF"
}

# UI Messages
MESSAGES = {
    'ready': "Ready",
    'connecting': "Connecting to ClickUp...",
    'connected': "Connected successfully!",
    'connection_failed': "Connection failed",
    'no_token': "Please enter your auth token",
    'no_workspace': "Please select a workspace",
    'no_space': "Please select a space",
    'no_users': "Please select at least one user",
    'invalid_date': "Invalid date format. Use YYYY-MM-DD",
    'no_data': "No data to export. Please fetch data first.",
    'export_complete': "Export completed successfully!",
    'export_failed': "Export failed"
}