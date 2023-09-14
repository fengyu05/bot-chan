from langchain import OpenAI

from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.tools.python.tool import PythonREPLTool
from botchan import settings
from botchan.tools.serp_api import create_serp_tool
from botchan.tools.llm_math import create_math_tool


def create_default_agent(
    allow_serp_search: bool = True,
    allow_llm_math: bool = True,
    allow_python_repl: bool = False,
):
    llm = OpenAI(temperature=0)
    tools = []
    if settings.SERPAPI_API_KEY and allow_serp_search:
        tools.append(create_serp_tool())

    if allow_llm_math:
        tools.append(create_math_tool())

    if allow_python_repl:
        tools.append(PythonREPLTool())

    mrkl = initialize_agent(
        tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )
    return mrkl
