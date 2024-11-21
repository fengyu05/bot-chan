from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import BaseMessage, HumanMessage

from fluctlight.embedding.chroma import get_chroma
from fluctlight.character_model.base import AsyncCallbackAudioHandler, AsyncCallbackTextHandler, ChatAgent
from fluctlight.logger import get_logger
from fluctlight.utt.timed import timed
from fluctlight.data_model.interface.character import Character
from langchain_community.chat_models import ChatOpenAI

logger = get_logger(__name__)


class OpenaiLlm(ChatAgent):
    def __init__(self, model: str, temperature: float = 0.5, openai_api_base: str | None = None, openai_api_key: str | None = None):
        self.chat_model = ChatOpenAI(
            model=model,
            temperature=temperature,
            streaming=True,
            openai_api_base=openai_api_base,
            openai_api_key=openai_api_key,
        )
        self.config = {"model": model, "temperature": temperature, "streaming": True, "openai_api_base": openai_api_base}
        self.db = get_chroma()

    @timed
    async def achat(
        self,
        history: list[BaseMessage],
        user_input: str,
        user_id: str,
        character: Character,
        callback: AsyncCallbackTextHandler,
        audioCallback: AsyncCallbackAudioHandler | None = None,
        metadata: dict | None = None,
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
        response = await self.chat_model.agenerate(
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
