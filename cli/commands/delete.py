"""
Command handler for deleting sessions.
"""

from . import CommandHandler


class DeleteCommand(CommandHandler):
    """Handle the 'delete <session_id>' command to delete a session."""
    
    @property
    def command_name(self) -> str:
        return "delete"
    
    @property
    def description(self) -> str:
        return "Delete a session (use with caution)"
    
    def execute(self, agent, args: str) -> bool:
        """Execute the delete command."""
        if not args:
            print("❌ Please specify a session ID to delete.")
            return True
        
        # Confirm deletion
        confirm = input(f"⚠️  Are you sure you want to delete session '{args}'? (yes/no): ")
        if confirm.lower() == "yes":
            success, message = agent._delete_session(args)
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
        else:
            print("❌ Deletion cancelled.")
        
        return True