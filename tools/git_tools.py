import os
from tools.base_tools import Tool
from langchain.tools import tool


def get_git_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@tool(
    name_or_callable="git_tool",
    description="It switches to the git root directory and runs the given git command. The executed command will be: git {command}",
)
def git_tool(command: str) -> str:
    return os.popen(f"cd {get_git_root()} && git {command}").read()
