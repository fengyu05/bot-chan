import os
from functools import cache

from langchain.chat_models.base import BaseChatModel

from fluctlight.character_model.base import ChatAgent
from fluctlight.character_model.openai_chat import OpenaiLlm

@cache
def get_chat_agent(model: str ="gpt-4o") -> ChatAgent:
    model = os.getenv("LLM_MODEL_USE", model)
    if model.startswith("gpt"):
        return OpenaiLlm(model=model)
    elif "local" in model:
        # Currently use llama2-wrapper to run local llama models
        local_llm_url = os.getenv("LOCAL_LLM_URL", "")
        if local_llm_url:
            return OpenaiLlm(model="local", openai_api_base=local_llm_url)
        else:
            raise ValueError("LOCAL_LLM_URL not set")
    else:
        raise ValueError(f"Invalid llm model: {model}")

@cache
def get_chat_model(model: str="gpt-4o") -> BaseChatModel:
    return get_chat_agent(model).chat_model

