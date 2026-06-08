"""
Command handler for loading sessions.
"""

from . import CommandHandler


class LoadCommand(CommandHandler):
    """Handle the 'load' command to load a session."""
    
    @property
    def command_name(self) -> str:
        return "load"
    
    @property
    def description(self) -> str:
        return "Load a session by ID"
    
    def execute(self, agent, args: str) -> bool:
        """Execute the load command."""
        if not args:
            print("\n❌ Usage: load <session_id>")
            print("   Example: load 20241215_143022")
            return True
        
        session_id = args.strip()
        success, message = agent.session_manager.load_session(session_id)
        
        if success:
            print(f"\n✅ {message}")
        else:
            print(f"\n❌ {message}")
        
        return True