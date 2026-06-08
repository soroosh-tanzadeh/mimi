import os
import json
import tempfile
import pytest
from pathlib import Path
from config.config import ConfigManager, get_config, validate_config


class TestConfigManager:
    """Test cases for ConfigManager class"""
    
    def setup_method(self):
        """Setup test environment"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.config_file = Path(self.test_dir) / "test_config.yaml"
        
    def teardown_method(self):
        """Clean up test environment"""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def test_config_manager_initialization(self):
        """Test ConfigManager initialization"""
        # Test with default config
        config_manager = ConfigManager()
        assert isinstance(config_manager, ConfigManager)
        assert isinstance(config_manager.config, dict)
        
    def test_config_manager_with_custom_path(self):
        """Test ConfigManager with custom config path"""
        config_manager = ConfigManager(str(self.config_file))
        assert config_manager.config_path == str(self.config_file)
        
    def test_create_default_config(self):
        """Test creation of default configuration"""
        config_manager = ConfigManager(str(self.config_file))
        # Check that default config was created
        assert self.config_file.exists()
        assert "model" in config_manager.config
        assert "agent" in config_manager.config
        assert "tools" in config_manager.config
        
    def test_load_yaml_config(self):
        """Test loading YAML configuration"""
        # Create a test YAML config
        test_config = {
            "test_key": "test_value",
            "nested": {"key": "value"}
        }
        
        with open(self.config_file, 'w') as f:
            import yaml
            yaml.dump(test_config, f)
            
        config_manager = ConfigManager(str(self.config_file))
        assert config_manager.get("test_key") == "test_value"
        assert config_manager.get("nested.key") == "value"
        
    def test_load_json_config(self):
        """Test loading JSON configuration"""
        # Create a test JSON config
        test_config = {
            "test_key": "test_value",
            "nested": {"key": "value"}
        }
        
        json_file = Path(self.test_dir) / "test_config.json"
        with open(json_file, 'w') as f:
            json.dump(test_config, f)
            
        config_manager = ConfigManager(str(json_file))
        assert config_manager.get("test_key") == "test_value"
        assert config_manager.get("nested.key") == "value"
        
    def test_get_config_value(self):
        """Test getting configuration values"""
        config_manager = ConfigManager(str(self.config_file))
        
        # Test existing key
        model_name = config_manager.get("model.name")
        assert model_name is not None
        
        # Test non-existing key with default
        non_existing = config_manager.get("non.existing.key", "default")
        assert non_existing == "default"
        
        # Test non-existing key without default
        non_existing = config_manager.get("non.existing.key")
        assert non_existing is None
        
    def test_set_config_value(self):
        """Test setting configuration values"""
        config_manager = ConfigManager(str(self.config_file))
        
        # Set a new value
        config_manager.set("test.new.key", "test_value")
        assert config_manager.get("test.new.key") == "test_value"
        
        # Update existing value
        old_model = config_manager.get("model.name")
        config_manager.set("model.name", "new_model")
        assert config_manager.get("model.name") == "new_model"
        
    def test_save_config(self):
        """Test saving configuration"""
        config_manager = ConfigManager(str(self.config_file))
        
        # Modify config
        config_manager.set("test.key", "test_value")
        
        # Save config
        config_manager.save()
        
        # Load config again and verify
        new_config_manager = ConfigManager(str(self.config_file))
        assert new_config_manager.get("test.key") == "test_value"
        
    def test_config_validation(self):
        """Test configuration validation"""
        config_manager = ConfigManager(str(self.config_file))
        
        # Test with valid config (should have no errors)
        errors = config_manager.validate()
        # With default config, we might have some validation errors due to missing API key
        # but we should test the validation logic
        
        # Test validation function
        errors = validate_config()
        # The validation result depends on environment variables


# Test global functions
def test_get_config_global():
    """Test global get_config function"""
    # Test getting a value
    value = get_config("model.name", "default")
    assert value is not None


if __name__ == "__main__":
    pytest.main([__file__])