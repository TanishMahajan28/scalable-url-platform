from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl
from sqlalchemy import insert
from shared.db import engine
from shared.models import links
from shared.redis import redis_client
from .utils import generate_code

router = APIRouter(prefix="/v1")

CACHE_TTL = 60 * 60


class CreateLinkRequest(BaseModel):
    long_url: HttpUrl


@router.post("/links")
async def create_link(req: CreateLinkRequest):
    short_code = generate_code()

    async with engine.begin() as conn:
        await conn.execute(
            insert(links).values(
                short_code=short_code,
                long_url=str(req.long_url),
            )
        )

    # Warm cache
    redis_client.setex(
        f"url:{short_code}",
        CACHE_TTL,
        str(req.long_url),
    )

    return {
        "short_code": short_code,
        "short_url": f"http://localhost:8000/{short_code}",
    }
