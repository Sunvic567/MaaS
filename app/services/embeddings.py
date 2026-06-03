from asyncio.log import logger
from app.core.config import Settings

settings = Settings()
embedder_setting = settings.embedder
BGE_PREFIX = settings.BGE_PREFIX


import time

def embed_for_storage(text: str, retries: int = 3, delay: float = 1.5) -> list[float]:
    prefixed = f"{BGE_PREFIX}{text}"
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            return embedder_setting.embed_query(prefixed)
        except Exception as e:
            last_error = e
            logger.warning(
                "Embedding attempt %d/%d failed: %s", attempt, retries, e
            )
            if attempt < retries:
                time.sleep(delay * attempt)  # 1.5s, 3s backoff

    raise RuntimeError(
        f"Embedding failed after {retries} attempts: {last_error}"
    )

def embed_for_search(text: str, retries: int = 3, delay: float = 1.5) -> list[float]:
    prefixed = f"{BGE_PREFIX}{text}"
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            return embedder_setting.embed_query(prefixed)
        except Exception as e:
            last_error = e
            logger.warning(
                "Embedding (search) attempt %d/%d failed: %s", attempt, retries, e
            )
            if attempt < retries:
                time.sleep(delay * attempt)

    raise RuntimeError(
        f"Search embedding failed after {retries} attempts: {last_error}"
    )


def _embed(text: str) -> list[float]:
    prefixed = f"{BGE_PREFIX}{text}"
    try:
        return embedder_setting.embed_query(prefixed)
    except Exception as e:
        print(f"  ⚠️  HuggingFace failed ({e}) — falling back to OpenAI")
        return _embed_openai_fallback(text)
    
def _embed_openai_fallback(text: str) -> list[float]:
    """
    Fallback when HuggingFace is down.
    NOTE: OpenAI text-embedding-3-small produces 1536-dim vectors.
    This fallback only works if your DB column is 1536 or larger.
    Since we're locked to 384, this fallback will fail at the DB level.
    Real fix: just retry HuggingFace or queue the request.
    For now — raise clearly instead of silently storing wrong dimensions.
    """
    raise RuntimeError(
        "HuggingFace embedding failed and no compatible fallback is available. "
        "Retry the request."
    )