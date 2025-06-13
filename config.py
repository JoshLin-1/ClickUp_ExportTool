
# API Configuration
CLICKUP_API_BASE_URL = "https://api.clickup.com/api/v2"
DEFAULT_HEADERS = {
    "Content-Type": "application/json"
}

# UI Configuration
WINDOW_TITLE = "ClickUp Data Export"
WINDOW_GEOMETRY = "700x600"
WINDOW_PADDING = "10"

# Excel Configuration
EXCEL_Max_SHEET_NAME_LENGTH = 31; 
EXCEL_COLUMN_MINWIDTH = 8; 
EXCEL_COLUMN_MAXWIDTH = 8; 

# Excel Configuration Headers 
EXCEL_HEADERS = {
    'date': '日期',
    'employee': '員工',
    'delivery': '專案',
    'workpackage': '工作包',
    'task':'任務',
    'description': '描述',
    'hours': '已花費工時',
    'url': 'URL'
}

# Excel Styling 
WORKSPACE_COLOR = "366092"
LIST_COLOR = "5B9BD5"
TASK_COLOR = "B4C6E7"
TOTAL_COLOR = "FF6B6B"

# Date format 
DATE_FORMAT = "%Y-%m-%d"
DEFAULT_TIME_PERIOD_DAYS = 7