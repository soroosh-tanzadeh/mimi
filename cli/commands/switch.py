"""
Command handler for switching sessions.
"""

from . import CommandHandler


class SwitchCommand(CommandHandler):
    """Handle the 'switch' command to switch to a different session."""
    
    @property
    def command_name(self) -> str:
        return "switch"
    
    @property
    def description(self) -> str:
        return "Switch to a different session"
    
    def execute(self, agent, args: str) -> bool:
        """Execute the switch command."""
        if not args:
            print("\n❌ Usage: switch <session_id>")
            print("   Example: switch 20241215_143022")
            return True
        
        session_id = args.strip()
        success, message = agent.session_manager.switch_session(session_id, agent.session_manager.thread_id)
        
        if success:
            print(f"\n✅ {message}")
        else:
            print(f"\n❌ {message}")
        
        return True