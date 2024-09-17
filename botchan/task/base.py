from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Type


class Task(ABC):
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
        return True

    def fallback_process(
        self, *args: Any, **kwds: Any
    ) -> Any:  # pylint: disable=unused-argument
        return None

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
        self,
        kwargs: dict[str, Any],
        key: str,
        message: Optional[str] = None,
        value_type: Optional[Type[Any]] = None,
    ) -> Any:
        if not message:
            message = f"task[{self.__class__.__name__}] input must has field {key}"
        assert key in kwargs, message
        if value_type is not None:
            assert isinstance(kwargs[key], value_type)
        return kwargs[key]
