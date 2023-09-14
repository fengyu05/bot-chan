from langchain import SerpAPIWrapper
from langchain.agents import Tool


def create_serp_tool() -> Tool:
    search = SerpAPIWrapper()
    return Tool(
        name="Search",
        func=search.run,
        description="useful for when you need to answer questions about current events. You should ask targeted questions",
    )
