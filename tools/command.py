import json
import os
import re
from pathlib import Path
from langchain.tools import tool
from rich import print
import typer

@tool(
    name_or_callable="run_command",
    description="Execute arbitary command",
)
def run_command(command: str) -> str:
    print(f"`{command}`")
    
    planAccepted = typer.confirm("Mimi wants to execute the command above, do accept the execution?")
    if planAccepted:
        return "User Reject command execution"
    return os.popen(f"{command}").read()