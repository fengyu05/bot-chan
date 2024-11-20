import logging

import structlog

from fluctlight.settings import LOG_LEVEL

numeric_log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(level=numeric_log_level)


def get_logger(logger_name):
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.filter_by_level,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger(logger_name)
