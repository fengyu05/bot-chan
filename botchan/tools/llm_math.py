from langchain import LLMMathChain
from langchain.agents import Tool
from langchain import OpenAI


def create_math_tool() -> Tool:
    llm = OpenAI(temperature=0)
    llm_math_chain = LLMMathChain.from_llm(llm)
    return Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="useful for when you need to answer questions about math",
    )
