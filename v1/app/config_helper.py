import os
import json

CONFIG_FILE_NAME = "config.json"

def get_config_path():
    """Returns the absolute path to config.json in the same directory as this file."""
    dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(dir_path, CONFIG_FILE_NAME)

def get_default_config():
    """Returns the default connection settings."""
    return {
        "host": "localhost",
        "port": 3306,
        "database": "mysql",
        "user": "root",
        "password": "",
        "theme": "lightmode"
    }

def load_connection_details():
    """Loads connection settings from config.json. Returns defaults if file doesn't exist or is invalid."""
    config_path = get_config_path()
    if not os.path.exists(config_path):
        return get_default_config()
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Ensure all required keys are present, fallback to defaults if missing
            defaults = get_default_config()
            for key, default_val in defaults.items():
                if key not in config:
                    config[key] = default_val
            
            # Ensure port is an integer
            if "port" in config:
                try:
                    config["port"] = int(config["port"])
                except (ValueError, TypeError):
                    config["port"] = defaults["port"]
                    
            return config
    except Exception as e:
        print(f"Error reading connection settings: {e}")
        return get_default_config()

def save_connection_details(details):
    """Saves the provided connection settings dict to config.json."""
    config_path = get_config_path()
    try:
        # Validate details keys & types
        clean_details = {}
        defaults = get_default_config()
        
        clean_details["host"] = str(details.get("host", defaults["host"])).strip()
        
        try:
            clean_details["port"] = int(details.get("port", defaults["port"]))
        except (ValueError, TypeError):
            clean_details["port"] = defaults["port"]
            
        clean_details["database"] = str(details.get("database", defaults["database"])).strip()
        clean_details["user"] = str(details.get("user", defaults["user"])).strip()
        clean_details["password"] = str(details.get("password", defaults["password"]))
        clean_details["theme"] = str(details.get("theme", defaults["theme"])).strip()
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(clean_details, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving connection settings: {e}")
        return False
