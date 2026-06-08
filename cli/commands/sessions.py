"""
Command handler for listing sessions.
"""

from . import CommandHandler


class SessionsCommand(CommandHandler):
    """Handle the 'sessions' command to list all available sessions."""
    
    @property
    def command_name(self) -> str:
        return "sessions"
    
    @property
    def description(self) -> str:
        return "List all available sessions"
    
    def execute(self, agent, args: str) -> bool:
        """Execute the sessions command."""
        sessions = agent.session_manager.list_sessions()
        if not sessions:
            print("\n📁 No sessions found.")
            return True
        
        print(f"\n📁 Available Sessions ({len(sessions)}):")
        print("=" * 80)
        print(f"{'ID':<20} {'Timestamp':<25} {'Messages':<10} {'Tools':<10} {'Size':<10}")
        print("-" * 80)
        
        for session in sessions:
            session_id = session["session_id"]
            timestamp = session["timestamp"][:19] if len(session["timestamp"]) > 19 else session["timestamp"]
            messages = session["conversation_count"]
            tools = session["tool_usage_count"]
            size_kb = f"{session['size_bytes'] / 1024:.1f}KB"
            
            # Highlight current session
            if session_id == agent.session_manager.session_id:
                session_id = f"▶ {session_id}"
            
            print(f"{session_id:<20} {timestamp:<25} {messages:<10} {tools:<10} {size_kb:<10}")
        print("=" * 80)
        
        return True