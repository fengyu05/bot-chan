import base64
import os
import uuid
from functools import lru_cache
from urllib.parse import urlparse

import requests
import structlog

from botchan.settings import SLACK_APP_OAUTH_TOKENS_FOR_WS, TMP_PATH

logger = structlog.get_logger(__name__)


@lru_cache(maxsize=128)
def read_file_content(file_path: str, length: int = 0) -> str:
    with open(file_path, "r", encoding="utf8") as file:
        if length <= 0:
            return file.read()
        else:
            return file.read(length)


def download_slack_downloadable(
    url: str, token: str = SLACK_APP_OAUTH_TOKENS_FOR_WS
) -> str:
    filename = str(uuid.uuid4())
    # Extract the file extension from the URL
    parsed_url = urlparse(url)
    _, ext = os.path.splitext(parsed_url.path)
    # Default to .bin if no extension found
    if not ext:
        ext = ".bin"

    local_path = f"{TMP_PATH}/{filename}.{ext}"

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    with open(local_path, "wb") as f:
        f.write(response.content)

    logger.debug(
        "Downloaded slack file",
        url=url,
        local_path=local_path,
        filename=f"{filename}{ext}",
    )
    return local_path


def base64_encode_slack_image(
    url: str, token: str = SLACK_APP_OAUTH_TOKENS_FOR_WS
) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    return base64.b64encode(response.content).decode("utf-8")
