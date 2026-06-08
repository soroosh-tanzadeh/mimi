"""
Command handlers for the agent CLI.
"""

import importlib
import inspect
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List, Tuple


class CommandHandler(ABC):
    """Base class for all command handlers."""
    
    @property
    @abstractmethod
    def command_name(self) -> str:
        """Return the command name this handler responds to."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a brief description of the command."""
        pass
    
    @abstractmethod
    def execute(self, agent: Any, args: str) -> bool:
        """
        Execute the command.
        
        Args:
            agent: The agent instance
            args: The command arguments (everything after the command name)
            
        Returns:
            bool: True if the command was handled and execution should continue,
                  False if the agent should exit (e.g., quit command)
        """
        pass
    
    def get_help(self) -> str:
        """Get help text for this command."""
        return f"{self.command_name}: {self.description}"


class CommandRegistry:
    """Registry for command handlers."""
    
    def __init__(self):
        self._handlers: Dict[str, CommandHandler] = {}
    
    def register(self, handler: CommandHandler) -> None:
        """Register a command handler."""
        self._handlers[handler.command_name] = handler
    
    def get_handler(self, command_name: str) -> Optional[CommandHandler]:
        """Get a handler by command name."""
        return self._handlers.get(command_name)
    
    def get_all_handlers(self) -> List[CommandHandler]:
        """Get all registered handlers."""
        return list(self._handlers.values())
    
    def get_command_names(self) -> List[str]:
        """Get all registered command names."""
        return list(self._handlers.keys())


# Global registry instance
registry = CommandRegistry()


def parse_command_input(user_input: str) -> Tuple[str, str]:
    """
    Parse user input into command and arguments.
    
    Args:
        user_input: The raw user input
        
    Returns:
        Tuple of (command_name, args)
    """
    if not user_input or not user_input.strip():
        return "", ""
    
    # Handle multi-word commands
    user_input = user_input.strip()
    
    # Check for multi-word commands first
    if user_input.lower().startswith("session info"):
        return "session info", user_input[12:].strip()
    
    # For single-word commands, split on first space
    parts = user_input.split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    return command, args


def register_all_commands():
    """Register all available commands by importing them."""
    # Import command modules directly
    try:
        from . import sessions, load, switch, delete, session_info, status, threads, quit
        
        # Register each command handler
        registry.register(sessions.SessionsCommand())
        registry.register(load.LoadCommand())
        registry.register(switch.SwitchCommand())
        registry.register(delete.DeleteCommand())
        registry.register(session_info.SessionInfoCommand())
        registry.register(status.StatusCommand())
        registry.register(threads.ThreadsCommand())
        registry.register(quit.QuitCommand())
        registry.register(quit.ExitCommand())  # Register exit as alias
        
    except ImportError as e:
        print(f"Warning: Could not import command modules: {e}")


# Initialize the registry when this module is imported
register_all_commands()