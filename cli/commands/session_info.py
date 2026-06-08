"""
Command handler for showing session information.
"""

from . import CommandHandler


class SessionInfoCommand(CommandHandler):
    """Handle the 'session info' command to show current session details."""
    
    @property
    def command_name(self) -> str:
        return "session info"
    
    @property
    def description(self) -> str:
        return "Show information about current session"
    
    def execute(self, agent, args: str) -> bool:
        """Execute the session info command."""
        info = agent.session_manager.get_session_info()
        
        print("\n📋 Session Information:")
        print("=" * 40)
        for key, value in info.items():
            print(f"  • {key}: {value}")
        
        return True