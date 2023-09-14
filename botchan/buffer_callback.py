# pylint: disable=abstract-method
from typing import Any, Dict, List
from langchain.callbacks import StdOutCallbackHandler


class BufferCallbackHandler(StdOutCallbackHandler):
    thought_buffer = []

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        if "text" in outputs:
            self.thought_buffer.extend(self.parse_text(outputs["text"]))

    def summary(self) -> str:
        return "\n".join(self.thought_buffer)

    @classmethod
    def parse_text(cls, text: str) -> List[str]:
        return text.split("\n")
