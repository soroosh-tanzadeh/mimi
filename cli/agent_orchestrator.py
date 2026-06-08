import os
from typing import Any, Dict, Optional
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage
from prompt_toolkit import print_formatted_text, HTML

from cli.spinner import Spinner
from cli.checkpointer import setup_check_pointer
from utils.logger import logger
from config.config import get_config

from langchain.messages import HumanMessage, AIMessage, ToolMessage

class AgentOrchestrator:
    """Orchestrates agent lifecycle and execution."""
    
    def __init__(self, system_prompt: str, tools: list, session_manager: Any = None):
        self.system_prompt = system_prompt
        self.tools = tools
        self.session_manager = session_manager
        
        # Initialize model from config
        model_name = get_config("model.name", os.environ.get("MODEL", "google/gemma-3-27b-it"))
        model_api_key = get_config("model.api_key", os.environ.get("OPENAI_API_KEY"))
        model_base_url = get_config("model.base_url", os.environ.get("OPENAI_API_BASE_URL"))
        
        self.model = ChatOpenAI(
            model=model_name,
            base_url=model_base_url,
            api_key=model_api_key,
        )
        
        self.spinner = Spinner(message="Mimi is thinking")
        self.checkpointer = setup_check_pointer()
        
        # Create agent
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=self.system_prompt,
            checkpointer=self.checkpointer,
        )
        
        self.checkpointer.list
        logger.info("Agent orchestrator initialized")

    def execute_streaming(self, user_input: str, thread_id: str, track_tool_callback: callable = None) -> str:
        """
        Execute agent with streaming response.
        
        Args:
            user_input: User's input message
            thread_id: Conversation thread ID
            track_tool_callback: Optional callback to track tool usage
            
        Returns:
            The AI's response content
        """
        self.spinner.start()
        ai_message_content = ""
        
        try:
            stream = self.agent.stream(
                {"messages": [HumanMessage(content=user_input)]},
                {"configurable": {"thread_id": thread_id}},
                stream_mode="messages",
            )

            first_chunk = False
            current_response = ""
            
            try:
                for chunk, metadata in stream:
                    if isinstance(chunk, HumanMessage):
                        # Skip human messages in stream
                        continue
                    elif isinstance(chunk, AIMessage) and chunk.content:
                        if not first_chunk:
                            self.spinner.stop()
                        content = chunk.content
                        print(content, end="", flush=True)
                        current_response += content
                        ai_message_content += content
                        first_chunk = True
                    elif isinstance(chunk, ToolMessage):
                        if current_response != "":
                            print()
                        tool_name = getattr(chunk, 'name', 'unknown')
                        print(f"\n\ud83d\udd27 MiMi is executing {tool_name}...")
                        
                        # Track tool usage if callback provided
                        if track_tool_callback:
                            track_tool_callback(
                                tool_name=tool_name,
                                input_data=str(getattr(chunk, 'tool_input', '')),
                                output=chunk.content,
                                success=True
                            )
                        
                        current_response = ""

                if ai_message_content:
                    print()
                    
            except KeyboardInterrupt:
                print("\n ❗ Response interrupted. Stopping stream...")
                self.spinner.stop()
            except Exception as e:
                logger.error(f"Streaming error: {e}", exc_info=True)
                print_formatted_text(HTML(f"<ansired>Streaming error: {str(e)}</ansired>"))
            finally:
                self.spinner.stop()
                
        except Exception as e:
            logger.error(f"Stream setup error: {e}", exc_info=True)
            print_formatted_text(HTML(f"<ansired>Error: {str(e)}</ansired>"))
            self.spinner.stop()
        
        return ai_message_content