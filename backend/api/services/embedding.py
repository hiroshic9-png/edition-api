"""Embedding service — vector embeddings for semantic search."""
import os
import hashlib
from typing import Optional

# MVP: Use ChromaDB's built-in embedding (no OpenAI key needed for basic operation)
import chromadb

_client: Optional[chromadb.ClientAPI] = None


def get_chroma_client() -> chromadb.ClientAPI:
    """Get or create ChromaDB client (persistent storage)."""
    global _client
    if _client is None:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
        _client = chromadb.PersistentClient(path=persist_dir)
    return _client


def get_collection(tenant_id: str, collection_type: str = "episodes"):
    """Get or create a ChromaDB collection for a tenant."""
    client = get_chroma_client()
    collection_name = f"{tenant_id[:8]}_{collection_type}"
    # ChromaDB collection names must be 3-63 chars, alphanumeric + underscores
    collection_name = collection_name[:63]
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"tenant_id": tenant_id, "type": collection_type},
    )


def store_embedding(tenant_id: str, doc_id: str, text: str, metadata: dict = None):
    """Store a document with its embedding in ChromaDB."""
    collection = get_collection(tenant_id, "episodes")
    collection.upsert(
        ids=[doc_id],
        documents=[text],
        metadatas=[metadata or {}],
    )


def search_embeddings(tenant_id: str, query: str, n_results: int = 5) -> list[dict]:
    """Semantic search over stored documents."""
    collection = get_collection(tenant_id, "episodes")
    if collection.count() == 0:
        return []
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
    )
    return [
        {
            "id": results["ids"][0][i],
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
            "distance": results["distances"][0][i] if results["distances"] else None,
        }
        for i in range(len(results["ids"][0]))
    ]
