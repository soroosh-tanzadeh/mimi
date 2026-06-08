"""
Command handler for deleting sessions.
"""

from . import CommandHandler


class DeleteCommand(CommandHandler):
    """Handle the 'delete' command to delete a session."""
    
    @property
    def command_name(self) -> str:
        return "delete"
    
    @property
    def description(self) -> str:
        return "Delete a session by ID"
    
    def execute(self, agent, args: str) -> bool:
        """Execute the delete command."""
        if not args:
            print("\n❌ Usage: delete <session_id>")
            print("   Example: delete 20241215_143022")
            return True
        
        session_id = args.strip()
        success, message = agent.session_manager.delete_session(session_id)
        
        if success:
            print(f"\n✅ {message}")
        else:
            print(f"\n❌ {message}")
        
        return True