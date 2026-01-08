import os
import sys
from dotenv import load_dotenv

#######################################################
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from utils.intro import showIntro
from cli.spinner import Spinner
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit import print_formatted_text, HTML, ANSI

#######################################################

############## Agent ##############
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

######################################

####### Tools ########
from tools import git_tool, read_file, list_files, write_to_file

#####################

load_dotenv()


class Agent:
    def __init__(self, prompt):
        self.promptSession = PromptSession()
        self.prompt = prompt
        self.instruction = os.environ.get("INSTRUCTION", "You are a helpful assistant.")
        self.spinner = Spinner(message="MiMi is working...")

        self.model = ChatOpenAI(
            model=os.environ.get("MODEL", "gpt-3.5-turbo"),
            base_url=os.environ.get("OPENAI_API_BASE_URL"),
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        self._load_system_prompt()

        self.tools = [git_tool, read_file, list_files, write_to_file]

        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=self.system_prompt,
            debug=False,
        )

        self.conversation: list = []  # will hold HumanMessage/AIMessage

    def _load_system_prompt(self):
        # If instruction is a file path, load from file
        if self.instruction and os.path.exists(self.instruction):
            try:
                with open(self.instruction, "r") as f:
                    self.system_prompt = f.read()
            except Exception:
                self.system_prompt = self.instruction
        else:
            self.system_prompt = self.instruction

    def run(self):
        showIntro()
        while True:
            try:
                user_input = self.promptSession.prompt(
                    self.prompt, auto_suggest=AutoSuggestFromHistory()
                )

                if user_input.lower() in ("quit", "exit"):
                    break
                if user_input.lower() == "clear":
                    print("\033[H\033[J")
                    self.conversation = []  # optional: clear memory too
                    continue
                if not user_input:
                    continue

                self.conversation.append(HumanMessage(content=user_input))

                final_ai = None
                with self.spinner:
                    for event in self.agent.stream(
                        {"messages": self.conversation},
                        stream_mode="values",
                    ):
                        # show the latest message
                        eventMessage = event["messages"][-1]
                        if isinstance(eventMessage, ToolMessage):
                            print_formatted_text(
                                HTML(
                                    f"\n<ansiblue>MiMi is executing {eventMessage.name}</ansiblue>"
                                )
                            )

                        final_ai = eventMessage

                # 3) persist assistant message into history
                if final_ai is not None and isinstance(final_ai, AIMessage):
                    self.conversation.append(final_ai)
                    print_formatted_text(
                        HTML(f"\n<ansiblue>MiMi> </ansiblue>"), ANSI(final_ai.content)
                    )

            except KeyboardInterrupt:
                print("Use 'quit' command to exit.")
            except Exception as e:
                print_formatted_text(HTML(f"<ansired>Error: {str(e)}</ansired>"))
