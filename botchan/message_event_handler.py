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
        cant_handle_func: Optional[Callable] = None,
    ) -> None:
        self.accept_intentions = set(accept_intentions)
        self.handler_func = handler_func
        self.cant_handle_func = cant_handle_func

    def can_handle(self, intent: MessageIntent) -> bool:
        return intent in self.accept_intentions

    def handle(self, message_event: MessageEvent) -> None:
        intent = get_message_intent(message_event)
        if self.can_handle(intent):
            self.do_handle(message_event, intent)
        else:
            self.cant_handle(message_event, intent)

    def do_handle(self, message_event: MessageEvent, intent: MessageIntent) -> None:
        if self.handler_func:
            self.handler_func(message_event, intent)
        else:
            logger.info(
                "using MessageEventHandler base class handler and the handler_func is missing"
            )

    def cant_handle(self, message_event: MessageEvent, intent: MessageIntent) -> None:
        if self.cant_handle_func:
            self.cant_handle_func(message_event, intent)
