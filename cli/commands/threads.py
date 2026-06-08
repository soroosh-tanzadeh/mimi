"""
Command handler for showing thread information.
"""

from . import CommandHandler


class ThreadsCommand(CommandHandler):
    """Handle the 'threads' command to show thread information."""
    
    @property
    def command_name(self) -> str:
        return "threads"
    
    @property
    def description(self) -> str:
        return "Show thread information"
    
    def execute(self, agent, args: str) -> bool:
        """Execute the threads command."""
        print("\n🧵 Thread Information:")
        print("=" * 40)
        print(f"  • Current Thread ID: {agent.session_manager.thread_id}")
        print(f"  • Thread Persisted: {'Yes' if agent.session_manager.session_loaded_from_file else 'No'}")
        
        # Show if thread was restored from session
        if agent.session_manager.loaded_session_id:
            print(f"  • Restored from Session: {agent.session_manager.loaded_session_id}")
        
        return True