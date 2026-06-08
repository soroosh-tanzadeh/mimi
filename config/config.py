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
        if (
            model_name
            and "gemma" in model_name.lower()
            and not self.get("model.base_url")
        ):
            errors["model.base_url"] = "Base URL is required for Gemma models"

        # Validate instruction file exists if it's a file path
        instruction = self.get("agent.instruction")
        if instruction and not instruction.startswith("system-prompts/"):
            instruction_path = Path(instruction)
            if not instruction_path.exists():
                errors["agent.instruction"] = (
                    f"Instruction file not found: {instruction}"
                )

        return errors

def setup_dirs(manager: ConfigManager):
    """Setup directories from config"""
    db_path = manager.get("sqlite_db")
    if not os.path.exists(db_path):
        os.makedirs(name=db_path)
    
    log_dir = manager.get("agent.log_dir")
    if not os.path.exists(log_dir):
        os.makedirs(name=log_dir)
    
    session_path = manager.get("agent.session_dir")
    if not os.path.exists(session_path):
        os.makedirs(name=session_path)

config_manager = ConfigManager()
setup_dirs(config_manager)

def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return config_manager.get(key, default)


def validate_config() -> Dict[str, str]:
    """Validate configuration"""
    return config_manager.validate()
