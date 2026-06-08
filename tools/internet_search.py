from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain.tools import tool
from typing import Literal
import requests


@tool(description="Search internet using DuckdDuckGo")
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
):

    wrapper = DuckDuckGoSearchAPIWrapper(max_results=max_results)
    search = DuckDuckGoSearchResults(
        output_format="list", api_wrapper=wrapper, source=topic
    )

    """Run a web search"""
    return search.invoke(query)


@tool(description="Open a URL and return the content")
def fetch_url_content(url: str):
    r = requests.get(url=url)
    return str(r.content)
