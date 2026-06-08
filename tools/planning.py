import typer
from langchain.tools import tool
from rich.console import Console
from rich.markdown import Markdown

console = Console()

@tool(
    name_or_callable="show_plan",
    description="Shows the plan markdown to the user.",
)
def show_plan(plan_markdown: str) -> str:
    """
        Shows the plan markdown to the user.
        
    Args:
        plan_markdown (str): The plan in markdown format

    Returns:
        str: if plan accepted `Plan Accepted, continue`, otherwise, `Plan rejected, ask for clarifications`
        
    """
    
    md = Markdown(plan_markdown)
    console.print(md)
    
    planAccepted = typer.confirm("Do you accept the provided plan?")
    if planAccepted:
        return "Plan Accepted, continue"
    
    return "Plan rejected, ask for clarifications"


@tool(
    name_or_callable="show_markdown",
    description="Shows a markdown to the user.",
)
def show_markdown(markdown_str: str):
    """
        Shows the plan markdown to the user.
        
    Args:
        markdown_str (str): The markdown code

    Returns: Nothing
        
    """
    
    md = Markdown(markdown_str)
    console.print(md)