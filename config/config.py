import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ConfigManager:
    """Configuration manager supporting multiple formats and validation"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.environ.get("CONFIG_FILE", "config.yaml")
        self.config = {}
        self._load_config()

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
        def expand_dict(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str) and any(path_indicator in key.lower() for path_indicator in ['path', 'dir', 'file']):
                        obj[key] = self._expand_path(value)
                    elif isinstance(value, dict):
                        expand_dict(value)
                    elif isinstance(value, list):
                        expand_list(value)
            elif isinstance(obj, list):
                expand_list(obj)
                
        def expand_list(obj):
            for i, item in enumerate(obj):
                if isinstance(item, dict):
                    expand_dict(item)
                elif isinstance(item, list):
                    expand_list(item)
                elif isinstance(item, str):
                    obj[i] = self._expand_path(item)
                    
        expand_dict(self.config)

    def _create_default_config(self):
        """Create default configuration file"""
        default_config = {
            "sqlite_db": "~/.mimi/database/",
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
        if isinstance(value, str) and any(path_indicator in keys[-1].lower() for path_indicator in ['path', 'dir', 'file']):
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
        required_fields = ["model.name", "model.api_key", "agent.instruction"]

        for field in required_fields:
            if not self.get(field):
                errors[field] = f"Required field {field} is missing or empty"

        # Validate model configuration
        model_name = self.get("model.name")
        if model_name and not self.get("model.api_key"):
            errors["model.api_key"] = "API key is required for model"

        # Validate instruction file exists if it's a file path
        instruction = self.get("agent.instruction")
        if instruction and not instruction.startswith("system-prompts/"):
            instruction_path = Path(instruction)
            if not instruction_path.exists():
                errors["agent.instruction"] = (
                    f"Instruction file not found: {instruction}"
                )

        # Validate directories exist or can be created
        directories_to_check = [
            ("agent.session_dir", "Session directory"),
            ("agent.log_dir", "Log directory"),
            ("sqlite_db", "Database directory")
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