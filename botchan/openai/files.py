import openai
import requests
import uuid
from typing import Optional
from pathlib import Path
from openai import OpenAI
from openai.types import FileObject
import structlog

logger = structlog.getLogger(__name__)


def upload_file(file_path: str) -> FileObject:
    """
    Uploads a file to OpenAI's servers for fine-tuning purposes.

    Args:
        file_path (str): The local path to the file that needs to be uploaded.

    Returns:
        Optional[FileObject]: The file object if the upload is successful, otherwise None.
    """
    try:
        client = OpenAI()
        return client.files.create(
            file=Path(file_path),
            purpose="fine-tune",
        )
    except Exception as e:
        logger.error(f"An error occurred while uploading the file: {e}")
        return None


def download_file(url: str, local_filename: Optional[str] = None) -> Optional[str]:
    """
    Downloads a file from a specified URL and saves it locally.

    Args:
        url (str): The URL of the file to be downloaded.
        local_filename (Optional[str]): The local filename where the file will be saved. If None, a filename will be generated using UUID.

    Returns:
        Optional[str]: The local filename if the download is successful, otherwise None.
    """
    if local_filename is None:
        local_filename = f"{uuid.uuid4()}.dat"  # Generate a unique filename with UUID

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        with open(local_filename, "wb") as file:
            file.write(response.content)
        return local_filename
    except requests.RequestException as e:
        logger.error(f"An error occurred while downloading the file", exc_info=e)
        return None


def upload_from_url(
    url: str, local_filename: Optional[str] = None
) -> Optional[FileObject]:
    """
    Downloads a file from a given URL and then uploads it to OpenAI's servers.

    Args:
        url (str): The URL of the file to be downloaded.
        local_filename (str): The local filename where the downloaded file will be saved.

    Returns:
        Optional[FileObject]: The file object if both the download and upload are successful, otherwise None.
    """
    downloaded_file = download_file(url, local_filename)

    if downloaded_file:
        file_object = upload_file(downloaded_file)
        if file_object:
            logger.info("File uploaded successfully.", url=url, file_object=file_object)
            return file_object
        else:
            logger.error("Failed to upload the file.", url=url)
            return None
    else:
        logger.error("Failed to download the file.", url=url)
        return None
