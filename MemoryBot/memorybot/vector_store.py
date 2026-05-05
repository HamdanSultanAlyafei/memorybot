"""
Pinecone + sentence-transformers integration — the long-term memory brain.

Design
------
• Embeddings: sentence-transformers all-MiniLM-L6-v2  (384 dims, runs locally,
  no extra API key required)
• Index: Pinecone Serverless (free tier: 1 index, 100k vectors)
• Each stored vector represents ONE compressed summary of ≥10 messages.
  Metadata: { "user_id": str, "summary": str, "created_at": str }
• On each new message we query Pinecone for the top-K most relevant past
  summaries and prepend them to the prompt.
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EMBEDDING_MODEL = "all-MiniLM-L6-v2"   # 384-dim, fast, free
EMBEDDING_DIM   = 384
CLOUD           = "aws"
REGION          = "us-east-1"


# ---------------------------------------------------------------------------
# Lazy singletons — models and clients are expensive to init
# ---------------------------------------------------------------------------

_embedder: Optional[SentenceTransformer] = None
_pinecone_client: Optional[Pinecone] = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder


def _get_pinecone(api_key: str) -> Pinecone:
    global _pinecone_client
    if _pinecone_client is None:
        _pinecone_client = Pinecone(api_key=api_key)
    return _pinecone_client


# ---------------------------------------------------------------------------
# Index management
# ---------------------------------------------------------------------------

def get_or_create_index(api_key: str, index_name: str):
    """Return a Pinecone Index object, creating the serverless index if needed."""
    pc = _get_pinecone(api_key)
    existing = [idx.name for idx in pc.list_indexes()]
    if index_name not in existing:
        pc.create_index(
            name=index_name,
            dimension=EMBEDDING_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud=CLOUD, region=REGION),
        )
    return pc.Index(index_name)


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------

def embed(text: str) -> list[float]:
    """Encode a string into a 384-dim vector."""
    return _get_embedder().encode(text, normalize_embeddings=True).tolist()


def store_memory(
    index,
    user_id: str,
    summary: str,
) -> str:
    """
    Embed `summary` and upsert it into Pinecone.
    Returns the vector ID so callers can track it.
    """
    vector_id = str(uuid.uuid4())
    vector     = embed(summary)
    metadata   = {
        "user_id":    user_id,
        "summary":    summary,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    index.upsert(vectors=[{"id": vector_id, "values": vector, "metadata": metadata}])
    return vector_id


def retrieve_memories(
    index,
    user_id: str,
    query: str,
    top_k: int = 3,
) -> list[str]:
    """
    Find the top_k most relevant past memories for this user given `query`.
    Returns a list of summary strings (empty list if Pinecone has nothing yet).
    """
    query_vec = embed(query)
    result = index.query(
        vector=query_vec,
        top_k=top_k,
        filter={"user_id": {"$eq": user_id}},
        include_metadata=True,
    )
    summaries = []
    for match in result.get("matches", []):
        meta = match.get("metadata", {})
        if summary := meta.get("summary"):
            summaries.append(summary)
    return summaries
