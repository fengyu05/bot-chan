import structlog
from langchain.chains.base import Chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from botchan.settings import OPENAI_GPT_MODEL_ID

logger = structlog.getLogger(__name__)


class ChatAgent:
    def __init__(self) -> None:
        self.fallback_chain = self._create_fallback_chain()

    def qa(self, text: str) -> str:
        logger.debug("chat agent qa invoke", text=text)
        return self.fallback_chain.invoke(text)

    def _create_fallback_chain(self) -> Chain:
        prompt = ChatPromptTemplate.from_template(
            "Please follow the instruction from users. {question}"
        )
        llm = ChatOpenAI(model_name=OPENAI_GPT_MODEL_ID, temperature=0)
        chain = (
            {
                "question": RunnablePassthrough(),
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        return chain
