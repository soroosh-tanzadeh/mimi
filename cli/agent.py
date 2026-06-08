import os
from rich import print
from uuid import uuid4

from dotenv import load_dotenv
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from utils.intro import showIntro
from cli.session_manager import SessionManager
from cli.agent_orchestrator import AgentOrchestrator
from utils.logger import logger
from config.config import get_config, validate_config
from tools import (
    git_tool,
    read_file,
    list_files,
    write_to_file,
    internet_search,
    fetch_url_content,
    show_plan,
    file_info,
    run_command,
    show_markdown
)

load_dotenv()


class Agent:
    """Main Agent class using refactored architecture."""
    
    def __init__(self, prompt=None):
        # Get configuration values
        self.config_prompt = get_config("agent.prompt", ">>> ")
        self.prompt = prompt or self.config_prompt
        self.prompt_session = PromptSession()
        
        # Validate configuration on startup
        config_errors = validate_config()
        if config_errors:
            print("\n⚠️  Configuration warnings:")
            for key, error in config_errors.items():
                print(f"  • {key}: {error}")
            print()

        # Initialize managers
        self.session_manager = SessionManager()
        
        # Initialize system prompt
        self.system_prompt = self._load_system_prompt()
        
        # Initialize tools
        self.tools = [
            git_tool,
            read_file,
            list_files,
            write_to_file,
            internet_search,
            fetch_url_content,
            show_plan,
            file_info,
            run_command,
            show_markdown
        ]
        
        # Initialize orchestrator
        self.orchestrator = AgentOrchestrator(
            system_prompt=self.system_prompt,
            tools=self.tools,
            session_manager=self.session_manager
        )
        
        # Generate thread ID if not loaded from session
        if not self.session_manager.thread_id:
            self.session_manager.thread_id = str(uuid4())
            logger.info(f"Generated new thread_id: {self.session_manager.thread_id}")
        else:
            logger.info(f"Using existing thread_id: {self.session_manager.thread_id}")

    def _load_system_prompt(self) -> str:
        """Load system prompt from file or config."""
        instruction = get_config("agent.instruction", os.environ.get("INSTRUCTION", "You are a helpful assistant."))
        
        if instruction and os.path.isfile(instruction):
            try:
                with open(instruction, "r", encoding="utf-8") as f:
                    system_prompt = f.read()
                logger.info(f"Loaded system prompt from {instruction}")
                return system_prompt
            except Exception as e:
                logger.error(f"Error loading system prompt from file: {e}")
        
        # Fallback: treat instruction as the prompt string
        logger.info("Using system prompt from environment/default")
        return instruction

    def run(self):
        """Main agent execution loop."""
        showIntro()
        logger.info("Agent started")
        
        # Import command handlers
        from cli.commands import registry, parse_command_input
        
        # Show available commands
        print("\n👋 Available commands:")
        for handler in registry.get_all_handlers():
            print(f"  \u2022 {handler.get_help()}")
        print()

        while True:
            try:
                user_input = self.prompt_session.prompt(
                    self.prompt,
                    auto_suggest=AutoSuggestFromHistory(),
                )

                # Check for quit/exit commands first (special handling)
                if user_input.lower().strip() in ("quit", "exit"):
                    logger.info("User requested exit")
                    print("\n\ud83d\udc4b Goodbye! Saving session...")
                    self.session_manager.save_session(self.session_manager.thread_id)
                    break

                # Parse command
                command, args = parse_command_input(user_input)
                
                # Skip empty input
                if not command:
                    continue
                
                # Handle commands
                handler = registry.get_handler(command)
                if handler:
                    logger.info(f"Executing command: {command} with args: {args}")
                    
                    # Execute command handler
                    should_continue = handler.execute(self, args)
                    
                    # If handler returns False, exit the agent
                    if not should_continue:
                        break
                    
                    continue
                
                # If no command handler found, treat as regular user input
                if not user_input.strip():
                    continue

                logger.info(f"User input: {user_input}")
                
                # Add to conversation
                from langchain.messages import HumanMessage, AIMessage
                self.session_manager.conversation.append(HumanMessage(content=user_input))

                # Execute streaming response
                ai_response = self.orchestrator.execute_streaming(
                    user_input=user_input,
                    thread_id=self.session_manager.thread_id,
                    track_tool_callback=self.session_manager.track_tool_usage
                )
                
                # Add AI response to conversation
                if ai_response:
                    self.session_manager.conversation.append(AIMessage(content=ai_response))
                    
            except KeyboardInterrupt:
                print("\n\n\☀️ Interrupted by user. Use 'quit' to exit.")
                continue
            except Exception as e:
                logger.error(f"Error in agent execution: {str(e)}", exc_info=True)
                print(f"Error: {str(e)}")


if __name__ == "__main__":
    agent = Agent()
    agent.run()