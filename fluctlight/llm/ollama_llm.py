import os
from typing import Optional

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage

from fluctlight.embedding.chroma import get_chroma
from fluctlight.llm.base import AsyncCallbackAudioHandler, AsyncCallbackTextHandler, LLM
from fluctlight.logger import get_logger
from fluctlight.utt.timed import timed, get_timer
from fluctlight.data_model.interface.character import Character


logger = get_logger(__name__)


class OllamaLlm(LLM):
    def __init__(self, model):
        self.chat_open_ai = ChatOpenAI(
            model=model,
            temperature=0.5,
            streaming=True,
            openai_api_base=os.getenv("OLLAMA_LLM_API_BASE")+"/v1",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.config = {"model": model, "temperature": 0.5, "streaming": True}
        self.db = get_chroma()

    def get_config(self):
        return self.config

    @timed
    async def achat(
        self,
        history: list[BaseMessage],
        user_input: str,
        user_id: str,
        character: Character,
        callback: AsyncCallbackTextHandler,
        audioCallback: Optional[AsyncCallbackAudioHandler] = None,
        metadata: Optional[dict] = None,
        *args,
        **kwargs,
    ) -> str:
        # 1. Generate context
        context = self._generate_context(user_input, character)

        # 2. Add user input to history
        history.append(
            HumanMessage(
                content=character.llm_user_prompt.format(context=context, query=user_input)
            )
        )

        # 3. Generate response
        callbacks = [callback, StreamingStdOutCallbackHandler()]
        if audioCallback is not None:
            callbacks.append(audioCallback)
        response = await self.chat_open_ai.agenerate(
            [history], callbacks=callbacks, metadata=metadata
        )
        logger.info(f"Response: {response}")
        return response.generations[0][0].text

    def _generate_context(self, query, character: Character) -> str:
        docs = self.db.similarity_search(query)
        docs = [d for d in docs if d.metadata["character_name"] == character.name]
        logger.info(f"Found {len(docs)} documents")

        context = "\n".join([d.page_content for d in docs])
        return context
