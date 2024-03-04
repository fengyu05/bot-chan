import uuid
from functools import lru_cache

import requests

from botchan.settings import SLACK_APP_OAUTH_TOKENS_FOR_WS, TMP_PATH


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
    local_path = f"{TMP_PATH}/{filename}.pdf"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    with open(local_path, "wb") as f:
        f.write(response.content)

    return local_path
