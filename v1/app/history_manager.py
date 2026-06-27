import os
import json
from datetime import datetime

# Resolve path relative to the directory containing this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_PATH = os.path.join(BASE_DIR, "query_history.json")

def load_history():
    """Load the query execution history from query_history.json."""
    if not os.path.exists(HISTORY_PATH):
        return []
    
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        # Return empty list in case of corruption
        return []

def log_query(sql, execution_time_ms, status, error_message=""):
    """Append a new query execution event to query_history.json.
    
    Args:
        sql (str): The SQL statement executed.
        execution_time_ms (int/float): The time it took to run.
        status (str): "Success" or "Error".
        error_message (str): Optional details if status is "Error".
    """
    event = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sql": sql,
        "execution_time_ms": execution_time_ms,
        "status": status,
        "error_message": error_message
    }
    
    history = load_history()
    history.append(event)
    
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)
        return True
    except OSError:
        return False

def clear_history():
    """Clear all query execution history."""
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)
        return True
    except OSError:
        return False
