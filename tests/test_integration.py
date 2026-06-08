import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from cli.agent import Agent


class TestIntegration:
    """Integration tests for the agent"""
    
    def setup_method(self):
        """Setup test environment"""
        pass
        
    def teardown_method(self):
        """Clean up test environment"""
        pass
        
    def test_agent_creation(self):
        """Test that agent can be created without errors"""
        with patch('cli.agent.load_dotenv'), \
             patch('cli.agent.ChatOpenAI'), \
             patch('cli.agent.create_agent'):
            
            # This should not raise any exceptions
            agent = Agent("Test> ")
            assert agent is not None
            
    def test_config_loading(self):
        """Test that configuration can be loaded"""
        from config.config import config_manager
        
        # Test that config manager loads without errors
        assert config_manager is not None
        assert isinstance(config_manager.config, dict)
        
    def test_session_directory_creation(self):
        """Test that session directory is created"""
        with patch('cli.agent.load_dotenv'), \
             patch('cli.agent.ChatOpenAI'), \
             patch('cli.agent.create_agent'):
            
            agent = Agent("Test> ")
            assert agent.session_dir.exists()
            
    def test_logger_initialization(self):
        """Test that logger is properly initialized"""
        from utils.logger import logger
        assert logger is not None


if __name__ == "__main__":
    pytest.main([__file__])