# pylint: disable=C0415
# pylint: disable=unused-import
"""CLI entrypoint."""

import click as click

from fluctlight.logger import get_logger

logger = get_logger(__name__)


@click.group()
def main() -> None:
    pass


@main.command()
def start() -> None:
    from fluctlight.server import start_server

    logger.debug("Debug log is on[if you see this]")
    start_server()
