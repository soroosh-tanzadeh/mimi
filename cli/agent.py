import os
import json
from rich import print
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from prompt_toolkit import PromptSession, print_formatted_text, HTML
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from langchain.agents import create_agent
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, AIMessage, ToolMessage

from utils.intro import showIntro
from cli.spinner import Spinner
from cli.checkpointer import setup_check_pointer
from utils.logger import logger
from tools import (
    git_tool,
    read_file,
    list_files,
    write_to_file,
    internet_search,
    fetch_url_content,
    show_plan,
    file_info,
    run_command
)

load_dotenv()


class Agent:
    def __init__(self, prompt, sessions_dir="~/.mimi/sessions"):
        self.prompt_session = PromptSession()
        self.prompt = prompt
        self.instruction = os.environ.get("INSTRUCTION", "You are a helpful assistant.")
        
        # Track conversation and tool usage for compatibility with tests
        self.conversation = []
        self.tool_usage_history = []
        
        # Session management
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = Path(sessions_dir)
        self.session_dir.mkdir(exist_ok=True)
        self.loaded_session_id = None  # Track which session was loaded
        self.session_loaded_from_file = False  # Track if session was loaded from file

        # Initialize model
        self.model = ChatOpenAI(
            model=os.environ.get("MODEL", "google/gemma-3-27b-it"),
            base_url=os.environ.get("OPENAI_API_BASE_URL"),
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        self._load_system_prompt()

        # Convert tools to LangChain Tool objects
        self.tools = [
            git_tool,
            read_file,
            list_files,
            write_to_file,
            internet_search,
            fetch_url_content,
            show_plan,
            file_info,
            run_command
        ]
        
        self.spinner = Spinner(message="Mimi is thinking")

        self.checkpointer = setup_check_pointer("./database/checkpointer.db")

        # Create agent using the non-deprecated import
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=self.system_prompt,  # parameter name may vary; adjust if needed
            checkpointer=self.checkpointer,
        )
        
        self.checkpointer.list

        # Generate a clean thread ID
        self.thread_id = str(uuid4())

    def _load_system_prompt(self):
        """Load system prompt from file or use the instruction string directly."""
        candidate = self.instruction
        if candidate and os.path.isfile(candidate):
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    self.system_prompt = f.read()
                logger.info(f"Loaded system prompt from {candidate}")
                return
            except Exception as e:
                logger.error(f"Error loading system prompt from file: {e}")
        # Fallback: treat instruction as the prompt string
        self.system_prompt = candidate
        logger.info("Using system prompt from environment/default")

    def _serialize_message(self, message):
        """Serialize a message for storage (compatibility with tests)."""
        if isinstance(message, HumanMessage):
            return {"type": "human", "content": message.content}
        elif isinstance(message, AIMessage):
            return {"type": "ai", "content": message.content}
        elif isinstance(message, ToolMessage):
            return {"type": "tool", "name": getattr(message, 'name', 'unknown'), 
                    "content": message.content}
        else:
            return {"type": "unknown", "content": str(message)}

    def _track_tool_usage(self, tool_name, input_data, output, success):
        """Track tool usage for analytics (compatibility with tests)."""
        self.tool_usage_history.append({
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "input": input_data,
            "output": output,
            "success": success
        })
        logger.info(f"Tool used: {tool_name} - Success: {success}")

    def _save_session(self):
        """Save session data to file (compatibility with tests)."""
        session_data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "conversation": [self._serialize_message(msg) for msg in self.conversation],
            "tool_usage": self.tool_usage_history
        }
        
        session_file = self.session_dir / f"{self.session_id}.json"
        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Session saved to {session_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False

    def _list_available_sessions(self):
        """List all available session files with metadata."""
        sessions = []
        try:
            for session_file in self.session_dir.glob("*.json"):
                try:
                    with open(session_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    session_id = session_file.stem
                    session_info = {
                        "session_id": session_id,
                        "filename": session_file.name,
                        "timestamp": data.get("timestamp", "Unknown"),
                        "conversation_count": len(data.get("conversation", [])),
                        "tool_usage_count": len(data.get("tool_usage", [])),
                        "size_bytes": session_file.stat().st_size
                    }
                    sessions.append(session_info)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Error reading session file {session_file.name}: {e}")
                    sessions.append({
                        "session_id": session_file.stem,
                        "filename": session_file.name,
                        "timestamp": "Invalid format",
                        "conversation_count": 0,
                        "tool_usage_count": 0,
                        "size_bytes": session_file.stat().st_size,
                        "error": str(e)
                    })
            
            # Sort by timestamp (newest first)
            sessions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return sessions
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return []

    def _load_session(self, session_id):
        """Load a session from file and restore conversation/tool usage history."""
        session_file = self.session_dir / f"{session_id}.json"
        
        if not session_file.exists():
            logger.error(f"Session file not found: {session_file}")
            return False, f"Session '{session_id}' not found"
        
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Validate session data structure
            if "conversation" not in data or "tool_usage" not in data:
                logger.error(f"Invalid session format in {session_id}")
                return False, f"Invalid session format in '{session_id}'"
            
            # Clear current conversation and tool usage
            self.conversation = []
            self.tool_usage_history = []
            
            # Restore conversation messages
            for msg_data in data.get("conversation", []):
                if msg_data.get("type") == "human":
                    self.conversation.append(HumanMessage(content=msg_data.get("content", "")))
                elif msg_data.get("type") == "ai":
                    self.conversation.append(AIMessage(content=msg_data.get("content", "")))
                elif msg_data.get("type") == "tool":
                    self.conversation.append(ToolMessage(
                        content=msg_data.get("content", ""),
                        name=msg_data.get("name", "unknown")
                    ))
            
            # Restore tool usage history
            self.tool_usage_history = data.get("tool_usage", [])
            
            # Update session tracking
            self.loaded_session_id = session_id
            self.session_loaded_from_file = True
            
            logger.info(f"Loaded session '{session_id}' with {len(self.conversation)} messages")
            return True, f"Session '{session_id}' loaded successfully with {len(self.conversation)} messages"
            
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return False, f"Error loading session '{session_id}': {str(e)}"

    def _switch_to_session(self, session_id):
        """Switch to a different session (saves current, loads new)."""
        # Save current session first
        if len(self.conversation) > 0 or len(self.tool_usage_history) > 0:
            print(f"💾 Saving current session '{self.session_id}'...")
            self._save_session()
        
        # Load new session
        success, message = self._load_session(session_id)
        if success:
            # Update session ID to the loaded one
            self.session_id = session_id
            print(f"✅ Switched to session '{session_id}'")
        return success, message

    def _delete_session(self, session_id):
        """Delete a session file."""
        session_file = self.session_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return False, f"Session '{session_id}' not found"
        
        try:
            # Prevent deleting currently loaded session
            if self.loaded_session_id == session_id or self.session_id == session_id:
                return False, f"Cannot delete currently active session '{session_id}'"
            
            session_file.unlink()
            logger.info(f"Deleted session file: {session_file}")
            return True, f"Session '{session_id}' deleted successfully"
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False, f"Error deleting session '{session_id}': {str(e)}"

    def _show_session_info(self):
        """Show detailed information about current session."""
        info = {
            "Current Session ID": self.session_id,
            "Loaded From File": "Yes" if self.session_loaded_from_file else "No",
            "Loaded Session ID": self.loaded_session_id if self.loaded_session_id else "None",
            "Conversation Messages": len(self.conversation),
            "Tool Usage Records": len(self.tool_usage_history),
            "Thread ID": self.thread_id,
            "Session Directory": str(self.session_dir.resolve())
        }
        
        print("\n📋 Session Information:")
        print("=" * 40)
        for key, value in info.items():
            print(f"  • {key}: {value}")

    def run(self):
        """Main agent execution loop."""
        showIntro()
        logger.info("Agent started")
        
        # Import command handlers
        from cli.commands import registry, parse_command_input
        
        # Show available commands
        print("\n📝 Available commands:")
        for handler in registry.get_all_handlers():
            print(f"  • {handler.get_help()}")
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
                    print("\n👋 Goodbye! Saving session...")
                    self._save_session()
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
                self.conversation.append(HumanMessage(content=user_input))

                # Stream using 'messages' mode for token-by-token output
                self.spinner.start()
                try:
                    stream = self.agent.stream(
                        {"messages": [HumanMessage(content=user_input)]},
                        {"configurable": {"thread_id": self.thread_id}},
                        stream_mode="messages",
                    )

                    first_chunk = False
                    current_response = ""
                    ai_message_content = ""
                    
                    try:
                        for chunk, metadata in stream:
                            if isinstance(chunk, AIMessage) and chunk.content:
                                if not first_chunk:
                                    self.spinner.stop()          # stop spinner as soon as we get first content
                                content = chunk.content
                                print(content, end="", flush=True)
                                current_response += content
                                ai_message_content += content
                                first_chunk = True
                            elif isinstance(chunk, ToolMessage):
                                if current_response != "":
                                    print()                      # finish any pending output
                                # Track tool usage
                                tool_name = getattr(chunk, 'name', 'unknown')
                                print(f"\n🔧 MiMi is executing {tool_name}...")
                                self._track_tool_usage(
                                    tool_name=tool_name,
                                    input_data=str(getattr(chunk, 'tool_input', '')),
                                    output=chunk.content,
                                    success=True
                                )
                                current_response = ""

                        if ai_message_content:
                            print()  # final newline after response
                            self.conversation.append(AIMessage(content=ai_message_content))

                    except KeyboardInterrupt:
                        print("\n⏸️   Response interrupted. Returning to prompt.")
                    except Exception as e:
                        logger.error(f"Streaming error: {e}", exc_info=True)
                        print_formatted_text(HTML(f"<ansired>Streaming error: {str(e)}</ansired>"))
                    finally:
                        self.spinner.stop()
                        
                except Exception as e:
                    logger.error(f"Stream setup error: {e}", exc_info=True)
                    print_formatted_text(HTML(f"<ansired>Error: {str(e)}</ansired>"))
                    self.spinner.stop()
                    
            except KeyboardInterrupt:
                print("\n\n🛑 Interrupted by user. Use 'quit' to exit.")
                continue
            except Exception as e:
                logger.error(f"Error in agent execution: {str(e)}", exc_info=True)
                print_formatted_text(HTML(f"<ansired>Error: {str(e)}</ansired>"))


if __name__ == "__main__":
    agent = Agent(prompt=">>> ")
    agent.run()