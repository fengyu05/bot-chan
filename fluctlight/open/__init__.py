import openai
from langsmith.wrappers import wrap_openai

from fluctlight.settings import TEST_MODE

if TEST_MODE:
    OPENAI_CLIENT = openai.OpenAI()
else:
    OPENAI_CLIENT = wrap_openai(openai.OpenAI())
