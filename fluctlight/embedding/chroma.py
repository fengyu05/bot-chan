from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from fluctlight.settings import OPENAI_API_KEY, CHROMA_DB_DIR, CHROMA_DB_COLLECTION_NAME
from fluctlight.logger import get_logger

logger = get_logger(__name__)


def get_chroma(embedding: bool = True):
    if embedding:
        embedding_function = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    else:
        embedding_function = None

    chroma = Chroma(
        collection_name=CHROMA_DB_COLLECTION_NAME,
        embedding_function=embedding_function,
        persist_directory=CHROMA_DB_DIR,
    )
    return chroma
