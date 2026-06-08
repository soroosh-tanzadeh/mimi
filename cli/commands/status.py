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
        return "Show agent status"
    
    def execute(self, agent, args: str) -> bool:
        """Execute the status command."""
        print(f"\n📊 Agent Status:")
        print(f"  • Session ID: {agent.session_id}")
        if agent.session_loaded_from_file:
            print(f"  • Loaded from: {agent.loaded_session_id}")
        print(f"  • Thread ID: {agent.thread_id}")
        print(f"  • Messages in session: {len(agent.conversation)}")
        print(f"  • Tools used: {len(agent.tool_usage_history)}")
        
        return True