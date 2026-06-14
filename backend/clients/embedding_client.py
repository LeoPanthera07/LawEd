import numpy as np

from backend.config import settings

_model = None

QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return _model


async def embed_query(query: str) -> list[float]:
    model = _get_model()
    prefixed = f"{QUERY_PREFIX}{query}"
    embedding = model.encode(prefixed, normalize_embeddings=True)
    return embedding.tolist()


def embed_passages(texts: list[str]) -> np.ndarray:
    model = _get_model()
    prefixed = [f"{PASSAGE_PREFIX}{t}" for t in texts]
    return model.encode(
        prefixed,
        batch_size=settings.EMBEDDING_BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
