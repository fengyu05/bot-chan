"""CLI entrypoint."""
import click

from botchan.index.indexer import create_index
from botchan.server import start_server
from botchan.settings import KNOWLEDGE_ACCEPT_PATTERN, KNOWLEDGE_FOLDER


@click.group()
def main() -> None:
    pass


@main.command()
def start() -> None:
    start_server()


@main.command()
@click.option(
    "--knowledge_folder",
    type=str,
    default=KNOWLEDGE_FOLDER,
    help="Path to the knowledge folder",
)
@click.option(
    "--file_extensions",
    type=str,
    multiple=True,
    default=KNOWLEDGE_ACCEPT_PATTERN,
    show_default=True,
    help="File extensions to process",
)
@click.option(
    "--confirm",
    is_flag=True,
    help="Confirm action to actually run the create_index function",
)
def index(knowledge_folder: str, file_extensions: tuple, confirm: bool) -> None:
    """Create index"""
    if confirm:
        create_index(knowledge_folder, file_extensions, dryrun=False)
    else:
        print("Running in dry-run mode. No changes will be made.")
        create_index(knowledge_folder, file_extensions, dryrun=True)
