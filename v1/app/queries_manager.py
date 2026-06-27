import os
import json
from .logs_tab import log_event

# Resolve path relative to the directory containing this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVED_QUERIES_PATH = os.path.join(BASE_DIR, "saved_queries.json")

DEFAULT_QUERIES = [
    {
        "name": "Show All Databases",
        "sql": "SHOW DATABASES;"
    },
    {
        "name": "Show Tables",
        "sql": "SHOW TABLES;"
    },
    {
        "name": "Show User Privileges",
        "sql": "SELECT User, Host FROM mysql.user;"
    },
    {
        "name": "Show Active Connections",
        "sql": "SHOW PROCESSLIST;"
    },
    {
        "name": "MySQL Version Info",
        "sql": "SELECT VERSION();"
    }
]

def load_queries():
    """Load queries from saved_queries.json. If the file doesn't exist, create it with default queries."""
    if not os.path.exists(SAVED_QUERIES_PATH):
        save_queries(DEFAULT_QUERIES)
        return DEFAULT_QUERIES
    
    try:
        with open(SAVED_QUERIES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return DEFAULT_QUERIES
    except (json.JSONDecodeError, OSError):
        # Fallback in case of corruption
        return DEFAULT_QUERIES

def save_queries(queries):
    """Save the list of queries to saved_queries.json."""
    try:
        with open(SAVED_QUERIES_PATH, "w", encoding="utf-8") as f:
            json.dump(queries, f, indent=4)
        return True
    except OSError:
        return False

def add_query(name, sql):
    """Add a new query to the saved queries list. Returns True if successful, False otherwise."""
    queries = load_queries()
    # Check if a query with this name already exists
    for q in queries:
        if q["name"].strip().lower() == name.strip().lower():
            # Already exists, we can update it or reject
            q["sql"] = sql
            log_event(f"Query updated: '{name}'", "QUERIES")
            return save_queries(queries)
    
    queries.append({"name": name, "sql": sql})
    log_event(f"Query added: '{name}'", "QUERIES")
    return save_queries(queries)

def delete_query(name):
    """Delete a query by name. Returns True if found and deleted, False otherwise."""
    queries = load_queries()
    initial_length = len(queries)
    queries = [q for q in queries if q["name"].strip().lower() != name.strip().lower()]
    if len(queries) < initial_length:
        log_event(f"Query deleted: '{name}'", "QUERIES")
        return save_queries(queries)
    return False

def update_query(old_name, new_name, sql):
    """Update an existing query's name and/or SQL. Returns True if successful, False otherwise."""
    queries = load_queries()
    for q in queries:
        if q["name"].strip().lower() == old_name.strip().lower():
            q["name"] = new_name
            q["sql"] = sql
            log_event(f"Query updated: '{old_name}' -> '{new_name}'", "QUERIES")
            return save_queries(queries)
    return False
