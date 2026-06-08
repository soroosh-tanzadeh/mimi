import os
from rich import print

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from prompt_toolkit import PromptSession, print_formatted_text, HTML
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from langchain.agents import create_agent
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
    show_plan
)

load_dotenv()


class Agent:
    def __init__(self, prompt):
        self.prompt_session = PromptSession()
        self.prompt = prompt
        self.instruction = os.environ.get("INSTRUCTION", "You are a helpful assistant.")
        # Spinner kept for potential future use
        self.spinner = Spinner(message="MiMi is working...")

        # Session management (reserved for future use)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = Path("sessions")
        self.session_dir.mkdir(exist_ok=True)

        # Initialize model
        self.model = ChatOpenAI(
            model=os.environ.get("MODEL", "google/gemma-3-27b-it"),
            base_url=os.environ.get("OPENAI_API_BASE_URL"),
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        self._load_system_prompt()

        self.tools = [
            git_tool,
            read_file,
            list_files,
            write_to_file,
            internet_search,
            fetch_url_content,
            show_plan
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

        # Generate a clean thread ID
        self.thread_id = str(uuid4())  # fixed from uuid4().bytes

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

    def run(self):
        """Main agent execution loop."""
        showIntro()
        logger.info("Agent started")
        streaming_active = False

        while True:
            try:
                user_input = self.prompt_session.prompt(
                    self.prompt,
                    auto_suggest=AutoSuggestFromHistory(),
                )

                if user_input.lower().strip() in ("quit", "exit"):
                    logger.info("User requested exit")
                    break

                if user_input.lower().strip() == "threads":
                    if hasattr(self.checkpointer, "list"):
                        print(self.checkpointer.list())
                    else:
                        print("Checkpointer does not support listing threads.")
                    continue

                if not user_input.strip():
                    continue

                logger.info(f"User input: {user_input}")

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
                    try:
                        for chunk, metadata in stream:
                            if isinstance(chunk, AIMessage) and chunk.content:
                                if not first_chunk:
                                    self.spinner.stop()          # stop spinner as soon as we get first content
                                content = chunk.content
                                print(content, end="", flush=True)
                                current_response += content
                                first_chunk = True
                            elif isinstance(chunk, ToolMessage):
                                if current_response:
                                    print()                      # finish any pending output
                                print(f"\n🔧 MiMi is executing {chunk.name}...")
                                current_response = ""

                        if current_response:
                            print()                              # final newline after response

                    except KeyboardInterrupt:
                        print("\n⏹️  Response interrupted. Returning to prompt.")
                    except Exception as e:
                        logger.error(f"Streaming error: {e}", exc_info=True)
                        print_formatted_text(HTML(f"<ansired>Streaming error: {str(e)}</ansired>"))
                    finally:
                        self.spinner.stop()
                        
                except Exception as e:
                    logger.error(f"Stream setup error: {e}", exc_info=True)
                    print_formatted_text(HTML(f"<ansired>Error: {str(e)}</ansired>"))
                    self.spinner.stop()
            except Exception as e:
                logger.error(f"Error in agent execution: {str(e)}", exc_info=True)
                print_formatted_text(HTML(f"<ansired>Error: {str(e)}</ansired>"))


if __name__ == "__main__":
    agent = Agent(prompt=">>> ")
    agent.run()
