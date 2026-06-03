import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from wrapt import lru_cache

load_dotenv()

class Settings:
    # Supabase client
    supabase = create_client(
        os.getenv("SUPABASE_URL", ""),
        os.getenv("SUPABASE_SERVICE_KEY", ""),
    )

    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "huggingface")
    # Embedding model
    embedder = HuggingFaceEndpointEmbeddings(
        model="BAAI/bge-small-en-v1.5",
        huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_KEY", ""),
    )

    # Constants
    RECENCY_DECAY_LAMBDA = 0.01
    AUTO_SUMMARISE_THRESHOLD = 100
    BGE_PREFIX = "Represent this sentence for searching relevant passages: "
    # Master key for admin endpoints (set in environment as MAAS_MASTER_KEY)
    MAAS_MASTER_KEY = os.getenv("MAAS_MASTER_KEY", "")
    # App environment
    app_env = os.getenv("ENVIRONMENT", "development")


@lru_cache
def get_settings() -> Settings:
    return Settings()