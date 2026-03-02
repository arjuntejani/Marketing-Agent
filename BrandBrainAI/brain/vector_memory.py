"""Vector memory utilities for storing and retrieving brand context embeddings.

Default backend is local ChromaDB with embeddings generated via local Ollama
embedding model HTTP API.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

import requests

try:
    import chromadb
except ImportError:  # pragma: no cover - dependency is expected in runtime env
    chromadb = None  # type: ignore[assignment]


class OllamaEmbedder:
    """Local embedding client using Ollama HTTP API."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mxbai-embed-large") -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def embed(self, text: str) -> list[float]:
        """Generate embedding vector for a single text input."""
        if not isinstance(text, str) or not text.strip():
            return []

        payload = {"model": self.model, "prompt": text}
        try:
            response = requests.post(f"{self.base_url}/api/embeddings", json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError, TypeError):
            return []

        embedding = data.get("embedding", [])
        return embedding if isinstance(embedding, list) else []


class VectorMemory:
    """Persistent vector memory built on local ChromaDB."""

    def __init__(
        self,
        persist_dir: str | Path = "memory/chroma",
        collection_name: str = "brand_memory",
        embedding_model: str = "mxbai-embed-large",
    ) -> None:
        if chromadb is None:
            raise RuntimeError("chromadb is not installed. Install chromadb to use VectorMemory.")

        base_dir = Path(__file__).resolve().parents[1]
        self.persist_dir = Path(persist_dir)
        if not self.persist_dir.is_absolute():
            self.persist_dir = base_dir / self.persist_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.embedder = OllamaEmbedder(model=embedding_model)
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def store_texts(self, texts: list[str], metadatas: list[dict[str, Any]] | None = None) -> int:
        """Embed and store texts. Returns number of successfully stored items."""
        if not texts:
            return 0

        cleaned: list[str] = []
        embeddings: list[list[float]] = []
        metadata_out: list[dict[str, Any]] = []
        ids: list[str] = []

        for idx, text in enumerate(texts):
            if not isinstance(text, str) or not text.strip():
                continue
            emb = self.embedder.embed(text)
            if not emb:
                continue
            cleaned.append(text.strip())
            embeddings.append(emb)
            ids.append(str(uuid4()))
            metadata_out.append((metadatas[idx] if metadatas and idx < len(metadatas) else {}) or {})

        if not cleaned:
            return 0

        self.collection.add(documents=cleaned, embeddings=embeddings, metadatas=metadata_out, ids=ids)
        return len(cleaned)

    def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Retrieve top_k closest vectors for a query."""
        query_embedding = self.embedder.embed(query)
        if not query_embedding:
            return []

        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        docs = (results.get("documents") or [[]])[0]
        metas = (results.get("metadatas") or [[]])[0]
        dists = (results.get("distances") or [[]])[0]

        out: list[dict[str, Any]] = []
        for i, doc in enumerate(docs):
            out.append(
                {
                    "document": doc,
                    "metadata": metas[i] if i < len(metas) else {},
                    "distance": dists[i] if i < len(dists) else None,
                }
            )
        return out


def build_from_artifacts(
    raw_text_path: str | Path = "memory/raw_text.txt",
    raw_products_path: str | Path = "memory/raw_products.json",
    top_n_products: int = 5,
) -> int:
    """Embed homepage text + top product snippets and store in local vector memory.

    Returns number of stored vector records.
    """
    base_dir = Path(__file__).resolve().parents[1]

    text_file = Path(raw_text_path)
    if not text_file.is_absolute():
        text_file = base_dir / text_file

    products_file = Path(raw_products_path)
    if not products_file.is_absolute():
        products_file = base_dir / products_file

    homepage_text = ""
    try:
        homepage_text = text_file.read_text(encoding="utf-8")
    except OSError:
        homepage_text = ""

    products: list[dict[str, Any]] = []
    try:
        payload = json.loads(products_file.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and isinstance(payload.get("products"), list):
            products = [p for p in payload["products"] if isinstance(p, dict)]
    except (OSError, json.JSONDecodeError):
        products = []

    texts: list[str] = []
    metas: list[dict[str, Any]] = []

    if homepage_text.strip():
        texts.append(homepage_text.strip())
        metas.append({"source": "homepage"})

    for product in products[:max(0, top_n_products)]:
        title = str(product.get("title", "")).strip()
        description = str(product.get("body_html", "")).strip()
        snippet = "\n".join([x for x in [title, description] if x]).strip()
        if not snippet:
            continue
        texts.append(snippet)
        metas.append({"source": "product", "title": title})

    if not texts:
        return 0

    vm = VectorMemory()
    return vm.store_texts(texts=texts, metadatas=metas)
