"""
Command handler for showing session information.
"""

from . import CommandHandler


class SessionInfoCommand(CommandHandler):
    """Handle the 'session info' command to show current session information."""
    
    @property
    def command_name(self) -> str:
        return "session info"
    
    @property
    def description(self) -> str:
        return "Show current session information"
    
    def execute(self, agent, args: str) -> bool:
        """Execute the session info command."""
        info = {
            "Current Session ID": agent.session_id,
            "Loaded From File": "Yes" if agent.session_loaded_from_file else "No",
            "Loaded Session ID": agent.loaded_session_id if agent.loaded_session_id else "None",
            "Conversation Messages": len(agent.conversation),
            "Tool Usage Records": len(agent.tool_usage_history),
            "Thread ID": agent.thread_id,
            "Session Directory": str(agent.session_dir.resolve())
        }
        
        print("\n📋 Session Information:")
        print("=" * 40)
        for key, value in info.items():
            print(f"  • {key}: {value}")
        
        return True