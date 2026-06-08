"""
Command handler for loading sessions.
"""

from . import CommandHandler


class LoadCommand(CommandHandler):
    """Handle the 'load <session_id>' command to load a session."""
    
    @property
    def command_name(self) -> str:
        return "load"
    
    @property
    def description(self) -> str:
        return "Load a session"
    
    def execute(self, agent, args: str) -> bool:
        """Execute the load command."""
        if not args:
            print("❌ Please specify a session ID to load.")
            return True
        
        success, message = agent._load_session(args)
        if success:
            print(f"✅ {message}")
            # Update session ID to the loaded one
            agent.session_id = args
        else:
            print(f"❌ {message}")
        
        return True