import logging
import time

logger = logging.getLogger(__name__)


def retry(action, retry_time_sec, retries=3):
    """
    Retry an action until it returns a non-None result or the retry limit is reached.

    Parameters:
    - action: The function to be retried.
    - retry_time_sec: The initial wait time between retries in seconds.
    - retries: The maximum number of retry attempts (default is 3).

    Returns:
    - The result of the action if successful, otherwise None after all retries.
    """
    attempt = 0
    delay = retry_time_sec

    while attempt < retries:
        result = action()
        if result is not None:
            return result

        logger.info(
            f"retry attempt {attempt + 1} failed. Retrying in {delay} seconds..."
        )
        time.sleep(delay)
        delay *= 2  # Double the wait time for the next retry
        attempt += 1

    logger.info("retry: All retries failed.")
    return None
