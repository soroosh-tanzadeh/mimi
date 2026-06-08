import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ConfigManager:
    """Configuration manager supporting multiple formats and validation"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.environ.get("CONFIG_FILE", "config.yaml")
        self.config = {}
        self._load_config()
        self._validate_environment()

    def _validate_environment(self):
        """Validate required environment variables"""
        required_env_vars = [
            "OPENAI_API_KEY",
            "OPENAI_API_BASE_URL",
            "MODEL"
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
            print("Please set these in your .env file or environment")
            # Don't crash, just warn - some might be provided in config file

    def _expand_path(self, path: str) -> str:
        """Expand user home directory and resolve relative paths."""
        if not path:
            return path
            
        # Expand ~ to home directory
        if path.startswith("~"):
            path = os.path.expanduser(path)
        
        # Resolve relative paths
        if not os.path.isabs(path):
            # Try to resolve relative to current working directory
            try:
                path = os.path.abspath(path)
            except Exception:
                pass
                
        return path

    def _is_path_key(self, key: str) -> bool:
        """Check if a configuration key is likely to be a path."""
        # More selective path detection
        path_keywords = ['path', 'dir', 'directory', 'file', 'db', 'log', 'session']
        
        # Check for exact matches or contains path indicators
        key_lower = key.lower()
        for keyword in path_keywords:
            if keyword in key_lower:
                # Exclude false positives
                if key_lower == 'log_level' or key_lower == 'log_dir':
                    return True
                if key_lower.endswith(keyword) or f"_{keyword}" in key_lower:
                    return True
        return False

    def _load_config(self):
        """Load configuration from file"""
        config_file = Path(self.config_path)

        if not config_file.exists():
            # Create default config if it doesn't exist
            self._create_default_config()
            return

        try:
            if config_file.suffix.lower() in [".yaml", ".yml"]:
                with open(config_file, "r") as f:
                    self.config = yaml.safe_load(f) or {}
            elif config_file.suffix.lower() == ".json":
                with open(config_file, "r") as f:
                    self.config = json.load(f)
            else:
                raise ValueError(
                    f"Unsupported config file format: {config_file.suffix}"
                )

        except Exception as e:
            print(f"Warning: Error loading config file: {e}")
            self.config = {}
            
        # Expand paths in the configuration
        self._expand_config_paths()

    def _expand_config_paths(self):
        """Expand all path-like configuration values."""
        def expand_dict(obj, parent_key=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    full_key = f"{parent_key}.{key}" if parent_key else key
                    if isinstance(value, str) and self._is_path_key(key):
                        obj[key] = self._expand_path(value)
                    elif isinstance(value, dict):
                        expand_dict(value, full_key)
                    elif isinstance(value, list):
                        expand_list(value, full_key)
            elif isinstance(obj, list):
                expand_list(obj, parent_key)
                
        def expand_list(obj, parent_key=""):
            for i, item in enumerate(obj):
                if isinstance(item, dict):
                    expand_dict(item, parent_key)
                elif isinstance(item, list):
                    expand_list(item, parent_key)
                elif isinstance(item, str) and self._is_path_key(parent_key):
                    obj[i] = self._expand_path(item)
                    
        expand_dict(self.config)

    def _create_default_config(self):
        """Create default configuration file"""
        default_config = {
            "sqlite_db": "~/.mimi/database/checkpointer.db",  # Fixed: Now a file path
            "model": {
                "name": os.environ.get("MODEL", "google/gemma-3-27b-it"),
                "api_key": os.environ.get("OPENAI_API_KEY", ""),
                "base_url": os.environ.get("OPENAI_API_BASE_URL", ""),
            },
            "agent": {
                "instruction": os.environ.get(
                    "INSTRUCTION", "system-prompts/code-assistant-prompt-planner.md"
                ),
                "session_dir": "~/.mimi/sessions",
                "log_level": "INFO",
                "log_dir": "~/.mimi/logs/",
                "prompt": "User> ",
            },
            "tools": {
                "allowed_directories": [".", "projects", "workspace"],
                "max_file_size": "10MB",
            },
        }

        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)

        if config_file.suffix.lower() in [".yaml", ".yml"]:
            with open(config_file, "w") as f:
                yaml.dump(default_config, f, default_flow_style=False)
        elif config_file.suffix.lower() == ".json":
            with open(config_file, "w") as f:
                json.dump(default_config, f, indent=2)

        self.config = default_config
        self._expand_config_paths()

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""
        keys = key.split(".")
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any):
        """Set configuration value with dot notation support"""
        keys = key.split(".")
        config = self.config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value
        
        # Expand path if it's a path-like configuration
        if isinstance(value, str) and self._is_path_key(keys[-1]):
            config[keys[-1]] = self._expand_path(value)

    def save(self):
        """Save configuration to file"""
        config_file = Path(self.config_path)

        if config_file.suffix.lower() in [".yaml", ".yml"]:
            with open(config_file, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False)
        elif config_file.suffix.lower() == ".json":
            with open(config_file, "w") as f:
                json.dump(self.config, f, indent=2)

    def validate(self) -> Dict[str, str]:
        """Validate configuration and return errors"""
        errors = {}

        # Check required fields
        required_fields = [
            "model.name", 
            "model.api_key", 
            "agent.instruction",
            "sqlite_db"
        ]

        for field in required_fields:
            value = self.get(field)
            if not value:
                errors[field] = f"Required field {field} is missing or empty"

        # Validate model configuration
        model_name = self.get("model.name")
        api_key = self.get("model.api_key")
        if model_name and not api_key:
            errors["model.api_key"] = "API key is required for model"

        # Validate instruction file exists if it's a file path
        instruction = self.get("agent.instruction")
        if instruction:
            # Check if it looks like a file path (not a URL or inline instruction)
            if "/" in instruction or instruction.endswith((".txt", ".md", ".yaml", ".yml")):
                instruction_path = Path(instruction)
                if not instruction_path.exists():
                    errors["agent.instruction"] = (
                        f"Instruction file not found: {instruction}"
                    )

        # Validate sqlite_db is a file path, not a directory
        sqlite_db = self.get("sqlite_db")
        if sqlite_db:
            expanded_path = self._expand_path(sqlite_db)
            if expanded_path.endswith("/"):
                errors["sqlite_db"] = "sqlite_db should be a file path, not a directory. Use 'checkpointer.db' as filename"
            else:
                # Ensure parent directory exists
                parent_dir = os.path.dirname(expanded_path)
                try:
                    os.makedirs(parent_dir, exist_ok=True)
                except Exception as e:
                    errors["sqlite_db"] = f"Cannot create database directory: {str(e)}"

        # Validate directories exist or can be created
        directories_to_check = [
            ("agent.session_dir", "Session directory"),
            ("agent.log_dir", "Log directory"),
        ]
        
        for key, description in directories_to_check:
            path = self.get(key)
            if path:
                try:
                    expanded_path = self._expand_path(path)
                    # Try to create directory if it doesn't exist
                    os.makedirs(expanded_path, exist_ok=True)
                except Exception as e:
                    errors[key] = f"{description} error: {str(e)}"

        return errors

    def get_expanded_path(self, key: str, default: Any = None) -> Any:
        """Get configuration value with path expansion"""
        value = self.get(key, default)
        if isinstance(value, str):
            return self._expand_path(value)
        return value


def setup_dirs(manager: ConfigManager):
    """Setup directories from config"""
    # Get expanded paths
    db_path = manager.get_expanded_path("sqlite_db")
    log_dir = manager.get_expanded_path("agent.log_dir")
    session_path = manager.get_expanded_path("agent.session_dir")
    
    # Create directories
    directories = [db_path, log_dir, session_path]
    for directory in directories:
        if directory:
            # For file paths, get the parent directory
            if os.path.isfile(directory) or not directory.endswith("/"):
                directory = os.path.dirname(directory)
            
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    print(f"Created directory: {directory}")
                except Exception as e:
                    print(f"Warning: Could not create directory {directory}: {e}")


config_manager = ConfigManager()
setup_dirs(config_manager)

def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return config_manager.get(key, default)


def validate_config() -> Dict[str, str]:
    """Validate configuration"""
    return config_manager.validate()


def get_expanded_path(key: str, default: Any = None) -> Any:
    """Get configuration value with path expansion"""
    return config_manager.get_expanded_path(key, default)