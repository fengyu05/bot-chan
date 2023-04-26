from typing import Callable, Optional, Sequence

import structlog

from botchan.slack.data_model import MessageEvent

from .message_intent import MessageIntent, get_message_intent

logger = structlog.getLogger(__name__)


class MessageEventHandler:
    accept_intentions: set(MessageIntent)

    def __init__(
        self,
        accept_intentions: Sequence[MessageIntent],
        handler_func: Optional[Callable] = None,
    ) -> None:
        self.accept_intentions = set(accept_intentions)
        self.handler_func = handler_func

    def can_handle(self, message_event: MessageEvent) -> bool:
        intention = get_message_intent(message_event)
        return intention in self.accept_intentions

    def handle(self, message_event: MessageEvent) -> None:
        if self.can_handle(message_event):
            self.do_handle(message_event)

    def do_handle(self, message_event: MessageEvent) -> None:
        if self.handler_func:
            self.handler_func(message_event)
        else:
            logger.info(
                "using MessageEventHandler base class handler and the handler_func is missing"
            )
