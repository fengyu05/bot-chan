# pylint: disable=C0415
# pylint: disable=unused-import
"""CLI entrypoint."""
import click
import structlog
import logging


def config_logger(log_level: str):
    # Convert log level string to upper case
    numeric_log_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure global logging level
    logging.basicConfig(level=numeric_log_level)

    # Configure structlog to respect the global logging level
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.JSONRenderer(),  # You can change to other formats if needed
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


@click.group()
def main() -> None:
    pass


@main.command()
@click.option(
    "--log-level", default="info", help="Set the logging level (default: info)"
)
def start(log_level: str) -> None:
    from botchan.server import start_server

    config_logger(log_level=log_level)
    start_server()

# Backdoor testing code block
@main.command()
def backdoor() -> None:
    pass
