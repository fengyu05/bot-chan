import openai
from langsmith.wrappers import wrap_openai

OPENAI_CLIENT = wrap_openai(openai.OpenAI())
