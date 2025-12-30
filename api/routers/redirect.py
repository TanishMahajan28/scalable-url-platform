from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from shared.redis import redis_client
from shared.db import engine
from shared.models import links

router = APIRouter()

CACHE_TTL = 60 * 60  # 1 hour


@router.get("/{short_code}")
async def redirect(short_code: str):
    cache_key = f"url:{short_code}"

    # Try Redis
    cached = redis_client.get(cache_key)
    if cached:
        return {"source": "cache", "long_url": cached}

    # Fallback to Postgres
    async with engine.connect() as conn:
        result = await conn.execute(
            select(links.c.long_url).where(
                links.c.short_code == short_code
            )
        )
        row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Short URL not found")

    long_url = row.long_url

    # Populate cache
    redis_client.setex(cache_key, CACHE_TTL, long_url)

    return {"source": "db", "long_url": long_url}
