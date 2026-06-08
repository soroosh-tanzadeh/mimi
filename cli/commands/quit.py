"""
Command handler for quitting the agent.
"""

from . import CommandHandler


class QuitCommand(CommandHandler):
    """Handle the 'quit' and 'exit' commands to exit the agent."""
    
    @property
    def command_name(self) -> str:
        return "quit"
    
    @property
    def description(self) -> str:
        return "Exit the agent"
    
    def execute(self, agent, args: str) -> bool:
        """Execute the quit command."""
        # Save session before exiting
        print("\n👋 Goodbye! Saving session...")
        agent._save_session()
        
        # Return False to indicate the agent should exit
        return False
    
    def get_help(self) -> str:
        """Override get_help to show both quit and exit."""
        return "quit/exit: Exit the agent"


class ExitCommand(CommandHandler):
    """Handle the 'exit' command (alias for quit)."""
    
    @property
    def command_name(self) -> str:
        return "exit"
    
    @property
    def description(self) -> str:
        return "Exit the agent (alias for quit)"
    
    def execute(self, agent, args: str) -> bool:
        """Execute the exit command - delegate to QuitCommand."""
        # Create a quit handler and use it
        quit_handler = QuitCommand()
        return quit_handler.execute(agent, args)