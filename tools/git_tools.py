import os
from langchain.tools import tool


def get_git_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@tool(
    name_or_callable="git_tool",
    description="It switches to the git root directory and runs the given git command. The executed command will be: git {command}",
)
def git_tool(command: str) -> str:
    """
    Execute a git command in the git root directory.

    This tool allows the agent to run git commands without needing to know the current directory structure.
    The tool automatically navigates to the git root directory before executing the command.

    Args:
        command (str): The git command to execute (without the 'git' prefix).
                       The agent should provide only the command part, e.g., "status", "log --oneline", "diff HEAD~1"

    Returns:
        str: The full output of the git command. The agent should parse this output to extract relevant information.
             If the command fails, the output will contain error messages that the agent can use for troubleshooting.

    Examples:
        git_tool("status")  # Executes "git status" to check repository status
        git_tool("log --oneline -5")  # Executes "git log --oneline -5" to get recent commit history
        git_tool("diff HEAD~1")  # Executes "git diff HEAD~1" to see changes since last commit

    Note:
        The agent should be aware that some git commands may produce no output if there are no changes or relevant information.
    """
    return os.popen(f"cd {get_git_root()} && git {command}").read()
