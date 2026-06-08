"""
Command handler for listing threads.
"""

from . import CommandHandler


class ThreadsCommand(CommandHandler):
    """Handle the 'threads' command to list available threads."""
    
    @property
    def command_name(self) -> str:
        return "threads"
    
    @property
    def description(self) -> str:
        return "List available threads"
    
    def execute(self, agent, args: str) -> bool:
        """Execute the threads command."""
        if hasattr(agent.checkpointer, "list"):
            for item in agent.checkpointer.list({"configurable":{"thread_id": agent.thread_id}}):
                print(item)
        else:
            print("Checkpointer does not support listing threads.")
        
        return True