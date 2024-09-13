from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from botchan.message_intent import MessageIntent


class Agent(ABC):
    def __init__(
        self,
        preprocess_hook: Optional[Callable] = None,
        postprocess_hook: Optional[Callable] = None,
    ) -> None:
        self.preprocess_hook = preprocess_hook
        self.postprocess_hook = postprocess_hook

    @abstractmethod
    def process(self, *args: Any, **kwds: Any) -> Any:
        pass

    def should_process(
        self, *args: Any, **kwds: Any
    ) -> bool:  # pylint: disable=unused-argument
        message_intent: MessageIntent = self._require_input(
            kwargs=kwds, key="message_intent"
        )
        return message_intent == self.intent

    def fallback_process(
        self, *args: Any, **kwds: Any
    ) -> Any:  # pylint: disable=unused-argument
        return None

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def intent(self) -> MessageIntent:
        pass

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if self.preprocess_hook:
            args, kwds = self.preprocess_hook(*args, **kwds)

        if self.should_process(*args, **kwds):
            result = self.process(*args, **kwds)
            if self.postprocess_hook:
                result = self.postprocess_hook(result)
            return result
        else:
            return self.fallback_process(*args, **kwds)

    def _require_input(
        self, kwargs: dict[str, Any], key: str, message: Optional[str] = None
    ) -> Any:
        if not message:
            message = f"Agent must has field {key}"
        assert key in kwargs, message
        return kwargs[key]
