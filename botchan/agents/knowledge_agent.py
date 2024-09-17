import structlog

from botchan.agents.message_intent_agent import MessageIntentAgent
from botchan.agents.openai_chat_agent import OpenAiChatAgent
from botchan.message_intent import MessageIntent
from botchan.rag.knowledge_base import KnowledgeBase
from botchan.rag.knowledge_doc import Doc, DocKind
from botchan.slack.data_model import FileObject, MessageEvent
from botchan.utt.regex import extract_all_urls

logger = structlog.getLogger(__name__)


class KnowledgeChatAgent(MessageIntentAgent):
    def __init__(self) -> None:
        super().__init__()
        self.base = KnowledgeBase()
        self.chat_agent = OpenAiChatAgent()

    def process_message(self, message_event: MessageEvent) -> list[str]:
        text = message_event.text
        if self.base.has_hit(text):
            return [self.base.chain.invoke(text)]
        else:
            return self.chat_agent(message_event=message_event)

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

    @property
    def description(self) -> str:
        return "Use to this agent to chat with context in RAG way"

    @property
    def name(self) -> str:
        return "KnowledgeChat"

    @property
    def intent(self) -> MessageIntent:
        return MessageIntent.KNOW
