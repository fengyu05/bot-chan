from typing import Optional
from enum import Enum

import structlog
import botchan.agents.prompt_bank as prompt_bank
from botchan.openai.files import upload_from_url
from botchan.slack.data_model import FileObject, MessageEvent
from botchan.settings import OPENAI_GPT_MODEL_ID, BOT_NAME
from botchan.utt.files import base64_encode_slack_image
from botchan.openai import CLIENT as client

logger = structlog.getLogger(__name__)




class OpenAiAssistantsAgent:
    def __init__(self) -> None:
        self.assistant = client.beta.assistants.create(
            name=BOT_NAME,
            description="You are a helpful assistant.",
            model=OPENAI_GPT_MODEL_ID,
            tools=[],
        )

    def new_thread(self, text: str):
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": text
                        }
                    ],
                }
            ]
        )
        logger.info("new thread", thread=thread)
        return thread

    def qa(self, message_event: MessageEvent) -> str:
        thread = self.new_thread(message_event.text)
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant.id
        )
        logger.info("thread run", run=run)




    def qa_with_image(self, message_event: MessageEvent) -> str:
        """
        Process a message event containing an image and return a response.

        This method processes the image in the message event and integrates it into
        the HumanMessage content before invoking the chain to generate a response.

        Args:
            message_event (MessageEvent): The message event to process, which contains both
                                          text and image data.

        Returns:
            str: The generated response.
        """
        logger.debug("chat agent qa invoke with image", text=message_event.text)
        images_data = self._process_image(message_event)

        message = HumanMessage(
            content=message_event.text,
            image=images_data[0]
        )
        response = self.chain.invoke([message])
        logger.debug("chat response", response=response)
        return response["response"]



    def _process_image(self, message_event: MessageEvent) -> list[str]:
        files = [
            file_object
            for file_object in message_event.files
            if self._accept_image_filetype(file_object)
        ]

        #return [base64_encode_slack_image(f.url_private_download) for f in files]
        return [upload_from_url(f.url_private_download, f.name).id for f in files]

    def _accept_image_filetype(self, file_object: FileObject) -> bool:
        return file_object.filetype.lower() in ("png", "jpg", "jpeg", "gif")
