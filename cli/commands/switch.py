"""
Command handler for switching sessions.
"""

from . import CommandHandler


class SwitchCommand(CommandHandler):
    """Handle the 'switch <session_id>' command to switch to a different session."""
    
    @property
    def command_name(self) -> str:
        return "switch"
    
    @property
    def description(self) -> str:
        return "Switch to a different session"
    
    def execute(self, agent, args: str) -> bool:
        """Execute the switch command."""
        if not args:
            print("❌ Please specify a session ID to switch to.")
            return True
        
        success, message = agent._switch_to_session(args)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
        
        return True