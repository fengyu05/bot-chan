from enum import Enum
from typing import Tuple

import structlog

from botchan.agents.openai_chat_agent import OpenAiChatAgent
from botchan.rag.knowledge_base import KnowledgeBase
from botchan.rag.knowledge_doc import Doc, DocKind
from botchan.slack.data_model import FileObject, MessageEvent
from botchan.utt.regex import extract_all_urls

logger = structlog.getLogger(__name__)

from botchan.settings import CHAT_MODE


class ResultType(Enum):
    RETRIEVAL = 1
    FALLBACK = 2


class KnowledgeChatAgent:
    def __init__(self) -> None:
        self.base = KnowledgeBase()
        self.fallback_agent = OpenAiChatAgent()

    def qa(self, message_event: MessageEvent) -> Tuple[ResultType, str]:
        text = message_event.text
        if CHAT_MODE == "RAG" and self.base.has_hit(text):
            return ResultType.RETRIEVAL, self.base.chain.invoke(text)
        else:
            return ResultType.FALLBACK, self.fallback_agent.qa(message_event)

    def learn_knowledge(self, message_event: MessageEvent) -> None:
        logger.debug("learn knowledge", message_event=message_event)
        if message_event.subtype == "file_share":
            self._learn_from_file(message_event)
            return

        urls = extract_all_urls(message_event.text)
        if urls:
            self.base.index_doc(
                [Doc(doc_kind=DocKind.WEB, source_url=url) for url in urls]
            )
            return
        self.base.index_doc([Doc(doc_kind=DocKind.TEXT, text=message_event.text)])

    def _learn_from_file(self, message_event: MessageEvent) -> None:
        files = [
            file_object
            for file_object in message_event.files
            if self._accept_file_type(file_object)
        ]
        self.base.index_doc(
            [
                Doc(
                    doc_kind=DocKind.PDF, source_url=f.url_private_download, name=f.name
                )
                for f in files
            ]
        )

    def _accept_file_type(self, file_object: FileObject) -> bool:
        return file_object.filetype == "pdf"
