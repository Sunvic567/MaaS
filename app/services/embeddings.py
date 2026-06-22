import os
import time
import logging
from openai import OpenAI
from app.core.config import Settings
from langchain_huggingface import HuggingFaceEndpointEmbeddings

settings = Settings()



logger          = logging.getLogger(__name__)
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
DIMENSIONS      = 384

_embedder = HuggingFaceEndpointEmbeddings(
    model=EMBEDDING_MODEL,
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
)


def embed_for_storage(text: str, retries: int = 3, delay: float = 1.5) -> list[float]:
    return _embed(text, retries, delay)


def embed_for_search(text: str, retries: int = 3, delay: float = 1.5) -> list[float]:
    return _embed(text, retries, delay)


def _embed(text: str, retries: int, delay: float) -> list[float]:
    prefixed = f"Represent this sentence for searching relevant passages: {text}"
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            return _embedder.embed_query(prefixed)
        except Exception as e:
            last_error = e
            logger.warning(
                "Embedding attempt %d/%d failed: %s", attempt, retries, e
            )
            if attempt < retries:
                time.sleep(delay * attempt)

    raise RuntimeError(
        f"Embedding failed after {retries} attempts: {last_error}"
    )




















# logger          = logging.getLogger(__name__)
# EMBEDDING_MODEL = "text-embedding-3-small"
# DIMENSIONS      = 1536

# client = OpenAI(api_key=settings.OPENAI_API_KEY)


# def embed_for_storage(text: str, retries: int = 3, delay: float = 1.5) -> list[float]:
#     return embed(text, retries, delay)


# def embed_for_search(text: str, retries: int = 3, delay: float = 1.5) -> list[float]:
#     return embed(text, retries, delay)


# def embed(text: str, retries: int, delay: float) -> list[float]:
#     last_error = None

#     for attempt in range(1, retries + 1):
#         try:
#             response = client.embeddings.create(
#                 model=EMBEDDING_MODEL,
#                 input=text,
#                 encoding_format="float",
#             )
#             return response.data[0].embedding
#         except Exception as e:
#             last_error = e
#             logger.warning(
#                 "Embedding attempt %d/%d failed: %s", attempt, retries, e
#             )
#             if attempt < retries:
#                 time.sleep(delay * attempt)

#     raise RuntimeError(
#         f"Embedding failed after {retries} attempts: {last_error}"
#     )