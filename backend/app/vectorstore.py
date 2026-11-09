import uuid
from functools import lru_cache

from qdrant_client import AsyncQdrantClient, models

from .config import get_settings


@lru_cache
def client() -> AsyncQdrantClient:
    settings = get_settings()
    if settings.qdrant_url == ":memory:":
        return AsyncQdrantClient(":memory:")
    return AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)


async def ensure_collection() -> None:
    settings = get_settings()
    qdrant = client()
    if await qdrant.collection_exists(settings.qdrant_collection):
        return
    await qdrant.create_collection(
        settings.qdrant_collection,
        vectors_config=models.VectorParams(size=settings.embed_dim, distance=models.Distance.COSINE),
    )
    for field in ("user_id", "doc_id"):
        await qdrant.create_payload_index(
            settings.qdrant_collection, field, models.PayloadSchemaType.KEYWORD
        )


async def add_chunks(doc_id: str, user_id: str, doc_name: str, chunks, vectors) -> None:
    settings = get_settings()
    points = [
        models.PointStruct(
            id=_point_id(doc_id, i),
            vector=vector,
            payload={
                "user_id": user_id,
                "doc_id": doc_id,
                "doc_name": doc_name,
                "page": chunk.page,
                "text": chunk.text,
            },
        )
        for i, (chunk, vector) in enumerate(zip(chunks, vectors))
    ]
    for start in range(0, len(points), 100):
        await client().upsert(settings.qdrant_collection, points[start : start + 100])


def _point_id(doc_id: str, index: int) -> str:
    return str(uuid.uuid5(uuid.UUID(doc_id), str(index)))


def _filter(user_id: str, doc_ids: list[str] | None) -> models.Filter:
    must = [models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id))]
    if doc_ids:
        must.append(models.FieldCondition(key="doc_id", match=models.MatchAny(any=doc_ids)))
    return models.Filter(must=must)


async def search(vector: list[float], user_id: str, doc_ids: list[str] | None, limit: int) -> list[dict]:
    result = await client().query_points(
        get_settings().qdrant_collection,
        query=vector,
        query_filter=_filter(user_id, doc_ids),
        limit=limit,
        with_payload=True,
    )
    return [{**p.payload, "score": p.score} for p in result.points]


async def delete_document(doc_id: str) -> None:
    await client().delete(
        get_settings().qdrant_collection,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[models.FieldCondition(key="doc_id", match=models.MatchValue(value=doc_id))]
            )
        ),
    )
