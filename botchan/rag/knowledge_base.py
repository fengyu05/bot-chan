# pylint: disable=E0611
# pylint: disable=broad-exception-caught
# pylint: disable=unsupported-binary-operation
import os

import bs4
import requests
import structlog
from langchain import hub
from langchain.chains.base import Chain
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from botchan.rag.knowledge_doc import Doc, DocKind
from botchan.settings import OPENAI_GPT_MODEL_ID
from botchan.utt.files import download_slack_downloadable

logger = structlog.getLogger(__name__)

_CHUNK_SIZE = 1000
_CHUNK_OVERLAP = 200


class KnowledgeBase:
    def __init__(self, debug: bool = False) -> None:
        self.vectorstore = FAISS.from_texts([""], embedding=OpenAIEmbeddings())
        self.chain = self._create_chain()
        self._debug = debug

    def _create_chain(self) -> Chain:
        retriever = self.vectorstore.as_retriever()
        prompt = hub.pull("rlm/rag-prompt")
        llm = ChatOpenAI(model_name=OPENAI_GPT_MODEL_ID, temperature=0)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        chain = (
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough(),
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        return chain

    def index_web(
        self,
        url: str,
        chunk_size: int = _CHUNK_SIZE,
        chunk_overlap: int = _CHUNK_OVERLAP,
    ) -> None:
        logger.debug("indexing web", url=url)
        loader = WebBaseLoader(
            web_paths=(url,),
            bs_kwargs={
                "parse_only": bs4.SoupStrainer(
                    ["div", "p", "li"]
                    # class_=("post-content", "post-title", "post-header")
                )
            },
        )
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        splits = text_splitter.split_documents(docs)
        logger.debug("web splits", splits=splits)
        self.vectorstore.add_documents(documents=splits)

    def index_pdf(self, url: str) -> None:
        logger.debug(f"indexing pdf {url}")
        try:
            local_path = download_slack_downloadable(url)
            loader = PyPDFLoader(local_path)
            pages = loader.load_and_split()
            self.vectorstore.add_documents(documents=pages)
            os.remove(local_path)
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
        except IOError as e:
            logger.error(f"File operation failed: {e}")
        except Exception as e:
            logger.exception(f"Unhandled error indexing pdf from {url}: {e}")

    def index_text(self, texts: list[str]) -> None:
        logger.debug("indexing text", texts=texts)
        self.vectorstore.add_texts(texts)

    def index_doc(self, docs: list[Doc]) -> None:
        if not docs:
            raise ValueError("The document list is empty.")

        # Check if all documents in the list have the same DocKind
        first_doc_kind = docs[0].doc_kind
        if not all(doc.doc_kind == first_doc_kind for doc in docs):
            raise ValueError("All documents must have the same DocKind.")

        for doc in docs:
            if doc.doc_kind == DocKind.TEXT:
                self.index_text(texts=[d.text for d in docs])
                ## index every in a batch
                break
            if doc.doc_kind == DocKind.WEB:
                self.index_web(url=doc.source_url)
            elif doc.doc_kind == DocKind.PDF:
                self.index_pdf(url=doc.source_url)
            else:
                raise ValueError(f"Index type {doc.doc_kind.name} not supported.")
