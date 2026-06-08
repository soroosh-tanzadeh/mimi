import pytest
import os
import json
from unittest.mock import Mock, patch
from cli.agent import Agent
from langchain.messages import HumanMessage, AIMessage


class TestAgent:
    """Test cases for Agent class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_prompt = "Test> "
        
    def test_agent_initialization(self):
        """Test Agent initialization"""
        with patch('cli.agent.load_dotenv'), \
             patch('cli.agent.ChatOpenAI'), \
             patch('cli.agent.create_agent'):
            
            agent = Agent(self.test_prompt)
            assert agent.prompt == self.test_prompt
            assert isinstance(agent.conversation, list)
            assert isinstance(agent.tool_usage_history, list)
            
    def test_serialize_message_human(self):
        """Test serialization of HumanMessage"""
        with patch('cli.agent.load_dotenv'), \
             patch('cli.agent.ChatOpenAI'), \
             patch('cli.agent.create_agent'):
            
            agent = Agent(self.test_prompt)
            message = HumanMessage(content="Hello")
            serialized = agent._serialize_message(message)
            
            assert serialized["type"] == "human"
            assert serialized["content"] == "Hello"
            
    def test_serialize_message_ai(self):
        """Test serialization of AIMessage"""
        with patch('cli.agent.load_dotenv'), \
             patch('cli.agent.ChatOpenAI'), \
             patch('cli.agent.create_agent'):
            
            agent = Agent(self.test_prompt)
            message = AIMessage(content="Hi there")
            serialized = agent._serialize_message(message)
            
            assert serialized["type"] == "ai"
            assert serialized["content"] == "Hi there"
            
    def test_track_tool_usage(self):
        """Test tool usage tracking"""
        with patch('cli.agent.load_dotenv'), \
             patch('cli.agent.ChatOpenAI'), \
             patch('cli.agent.create_agent'):
            
            agent = Agent(self.test_prompt)
            initial_count = len(agent.tool_usage_history)
            
            agent._track_tool_usage("test_tool", "input", "output", True)
            
            assert len(agent.tool_usage_history) == initial_count + 1
            last_record = agent.tool_usage_history[-1]
            assert last_record["tool_name"] == "test_tool"
            assert last_record["input"] == "input"
            assert last_record["output"] == "output"
            assert last_record["success"] == True
            
    def test_save_session(self):
        """Test session saving"""
        with patch('cli.agent.load_dotenv'), \
             patch('cli.agent.ChatOpenAI'), \
             patch('cli.agent.create_agent'):
            
            agent = Agent(self.test_prompt)
            agent.conversation = [HumanMessage(content="Hello")]
            
            # Mock the file operations
            with patch('cli.agent.open', create=True) as mock_open:
                mock_file = Mock()
                mock_open.return_value.__enter__.return_value = mock_file
                
                agent._save_session()
                
                # Check that write was called (multiple times due to JSON formatting)
                assert mock_file.write.call_count > 0
                
    def test_load_system_prompt_file(self):
        """Test loading system prompt from file"""
        with patch('cli.agent.load_dotenv'), \
             patch('cli.agent.ChatOpenAI'), \
             patch('cli.agent.create_agent'):
            
            agent = Agent(self.test_prompt)
            
            # Create a temporary prompt file
            test_prompt_content = "Test system prompt"
            with open("test_prompt.txt", "w") as f:
                f.write(test_prompt_content)
                
            agent.instruction = "test_prompt.txt"
            agent._load_system_prompt()
            
            # Clean up
            os.remove("test_prompt.txt")
            
            # The system prompt should be loaded from file
            assert agent.system_prompt == test_prompt_content
            
    def test_load_system_prompt_default(self):
        """Test loading default system prompt"""
        with patch('cli.agent.load_dotenv'), \
             patch('cli.agent.ChatOpenAI'), \
             patch('cli.agent.create_agent'):
            
            agent = Agent(self.test_prompt)
            agent.instruction = "Non-existent-file.txt"
            agent._load_system_prompt()
            
            # Should fall back to the instruction as system prompt
            assert agent.system_prompt == "Non-existent-file.txt"


if __name__ == "__main__":
    pytest.main([__file__])