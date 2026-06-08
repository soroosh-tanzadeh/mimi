"""
Command handler for showing agent status.
"""

from . import CommandHandler


class StatusCommand(CommandHandler):
    """Handle the 'status' command to show agent status."""
    
    @property
    def command_name(self) -> str:
        return "status"
    
    @property
    def description(self) -> str:
        return "Show current agent status"
    
    def execute(self, agent, args: str) -> bool:
        """Execute the status command."""
        from config.config import get_config
        
        print("\n📊 Agent Status:")
        print("=" * 40)
        
        # Model info
        model_name = get_config("model.name", "Not configured")
        print(f"  • Model: {model_name}")
        
        # Session info
        session_info = agent.session_manager.get_session_info()
        print(f"  • Session ID: {session_info['Current Session ID']}")
        print(f"  • Thread ID: {session_info['Thread ID']}")
        print(f"  • Messages: {session_info['Conversation Messages']}")
        print(f"  • Tools Used: {session_info['Tool Usage Records']}")
        
        # Memory info
        print(f"  • Session Directory: {session_info['Session Directory']}")
        
        return True