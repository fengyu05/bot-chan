import os
import unittest


def skip_integration_tests(func):
    """A decorator to skip integration tests by default."""

    def wrapper(*args, **kwargs):
        # Check some condition to decide whether to run or skip.
        # For instance, check if a certain environment flag is set.
        if os.getenv("RUN_INTEGRATION_TESTS", "0") == "1":
            return func(*args, **kwargs)
        else:
            raise unittest.SkipTest("Skipping integration test by default.")

    return wrapper
