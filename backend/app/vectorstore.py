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


async def reset_collection(name: str) -> None:
    qdrant = client()
    if await qdrant.collection_exists(name):
        await qdrant.delete_collection(name)
    await qdrant.create_collection(
        name,
        vectors_config=models.VectorParams(size=get_settings().embed_dim, distance=models.Distance.COSINE),
    )
    await qdrant.create_payload_index(name, "norma_id", models.PayloadSchemaType.KEYWORD)


async def count(name: str) -> int:
    qdrant = client()
    if not await qdrant.collection_exists(name):
        return 0
    return (await qdrant.count(name, exact=True)).count


async def add_points(name: str, items: list[dict], vectors: list[list[float]]) -> None:
    points = [
        models.PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{item['articulo_id']}#{item['chunk_idx']}")),
            vector=vector,
            payload=item,
        )
        for item, vector in zip(items, vectors)
    ]
    await client().upsert(name, points)


async def search(name: str, vector: list[float], limit: int) -> list[dict]:
    result = await client().query_points(name, query=vector, limit=limit, with_payload=True)
    return [{**p.payload, "score": p.score} for p in result.points]


async def drop_others(prefix: str, keep: str) -> None:
    qdrant = client()
    for c in (await qdrant.get_collections()).collections:
        if c.name.startswith(prefix) and c.name != keep:
            await qdrant.delete_collection(c.name)
