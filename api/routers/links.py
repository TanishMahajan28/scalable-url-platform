# from fastapi import APIRouter
# from pydantic import BaseModel, HttpUrl
# from sqlalchemy import insert
# from sqlalchemy.exc import IntegrityError
# from shared.db import engine
# from shared.models import links
# from shared.redis import redis_client
# from .utils import generate_code

# router = APIRouter(prefix="/v1")

# CACHE_TTL = 60 * 60


# class CreateLinkRequest(BaseModel):
#     long_url: HttpUrl


# @router.post("/links")
# async def create_link(req: CreateLinkRequest):
#     short_code = generate_code()

#     async with engine.begin() as conn:
#         await conn.execute(
#             insert(links).values(
#                 short_code=short_code,
#                 long_url=str(req.long_url),
#             )
#         )

#     # Warm cache
#     redis_client.setex(
#         f"url:{short_code}",
#         CACHE_TTL,
#         str(req.long_url),
#     )

#     return {
#         "short_code": short_code,
#         "short_url": f"http://localhost:8000/{short_code}",
#     }


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from shared.db import engine
from shared.models import links
from shared.redis import redis_client
from .utils import generate_code

router = APIRouter()

CACHE_TTL = 60 * 60
MAX_RETRIES = 5


class CreateLinkRequest(BaseModel):
    long_url: HttpUrl


@router.post("/links")
async def create_link(req: CreateLinkRequest):
    for attempt in range(MAX_RETRIES):
        short_code = generate_code()

        try:
            async with engine.begin() as conn:
                await conn.execute(
                    insert(links).values(
                        short_code=short_code,
                        long_url=str(req.long_url),
                    )
                )

            # Warm Redis cache AFTER successful DB commit
            redis_client.setex(
                f"url:{short_code}",
                CACHE_TTL,
                str(req.long_url),
            )

            return {
                "short_code": short_code,
                "short_url": f"http://localhost:8000/{short_code}",
            }

        except IntegrityError:
            # Collision detected — retry
            if attempt == MAX_RETRIES - 1:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate unique short code",
                )

            # Otherwise: retry with a new code
            continue
