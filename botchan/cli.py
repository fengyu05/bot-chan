# pylint: disable=C0415
"""CLI entrypoint."""
import click


@click.group()
def main() -> None:
    pass


@main.command()
def start() -> None:
    from botchan.server import start_server

    start_server()


@main.command()
def test() -> None:
    from botchan.rag.knowledge_base import KnowledgeBase
    from botchan.rag.knowledge_doc import Doc, DocKind

    base = KnowledgeBase()
    base.index_doc(
        [
            Doc(
                doc_kind=DocKind.PDF,
                source_url="https://files.slack.com/files-pri/T050B663C4C-F06MXKVDQBW/download/text_pdf__2_.pdf",
            )
        ]
    )
    print(base.chain.invoke("What is image synthesis"))
