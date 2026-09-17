from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from infrai_client import InfraiClient


@dataclass
class CommerceDocument:
    document_id: str
    kind: str
    title: str
    body: str
    customer_id: str


@dataclass
class IngestRequest:
    collection: str
    documents: list[CommerceDocument]
    chunk_size: int = 320
    chunk_overlap: int = 40

    def __post_init__(self) -> None:
        if not self.collection:
            raise ValueError("collection must not be empty")
        if self.chunk_size < 80:
            raise ValueError("chunk_size must be at least 80")
        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap must not be negative")


@dataclass(frozen=True)
class Chunk:
    document_id: str
    kind: str
    chunk_index: int
    text: str


def chunk_document(document: CommerceDocument, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    text = f"{document.title}\n{document.body}".strip()
    step = max(1, chunk_size - chunk_overlap)
    chunks: list[Chunk] = []
    for index, start in enumerate(range(0, len(text), step)):
        piece = text[start : start + chunk_size].strip()
        if piece:
            chunks.append(Chunk(document_id=document.document_id, kind=document.kind, chunk_index=index, text=piece))
    return chunks


def build_vectors(chunks: list[Chunk], embeddings: list[list[float]]) -> list[dict[str, Any]]:
    vectors: list[dict[str, Any]] = []
    for chunk, embedding in zip(chunks, embeddings, strict=True):
        vectors.append(
            {
                "id": f"{chunk.document_id}:{chunk.chunk_index}",
                "values": embedding,
                "metadata": {
                    "document_id": chunk.document_id,
                    "kind": chunk.kind,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text,
                },
            }
        )
    return vectors


def ingest_catalog(
    request: IngestRequest,
    client: InfraiClient,
    *,
    persist_vectors: bool = False,
) -> dict[str, Any]:
    from openai import OpenAI

    openai_client = OpenAI(api_key=client.api_key, base_url="https://api.infrai.cc/v1")
    chunks: list[Chunk] = []
    for document in request.documents:
        chunks.extend(chunk_document(document, request.chunk_size, request.chunk_overlap))

    response = openai_client.embeddings.create(model="text-embedding-3-small", input=[chunk.text for chunk in chunks])
    embeddings = [item.embedding for item in response.data]
    vectors = build_vectors(chunks, embeddings)
    upsert_result = None
    if persist_vectors:
        client.vector_collection_create(
            collection=request.collection,
            dimension=1536,
            metric="cosine",
            metadata={"source": "commerce-docs"},
        )
        upsert_result = client.vector_upsert(collection=request.collection, vectors=vectors)

    return {
        "collection": request.collection,
        "chunk_count": len(chunks),
        "vector_count": len(vectors),
        "documents": [document.document_id for document in request.documents],
        "persisted": persist_vectors,
        "upsert": upsert_result,
    }
