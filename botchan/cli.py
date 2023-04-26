"""CLI entrypoint."""
import click

from botchan.server import start_server


@click.group()
def main() -> None:
    pass


@main.command()
def start() -> None:
    start_server()
