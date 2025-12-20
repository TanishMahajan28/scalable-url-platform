from fastapi import APIRouter, HTTPException
from shared.redis import redis_client

router = APIRouter()

@router.get("/{code}")
async def redirect(code: str):
    # 1️⃣ Try Redis first
    cached_url = redis_client.get(f"code:{code}")
    if cached_url:
        return {
            "source": "cache",
            "long_url": cached_url,
        }

    # 2️⃣ DB fallback (mock for now)
    # TODO: replace with real Postgres lookup
    fake_db = {
        "abc123": "https://example.com"
    }

    long_url = fake_db.get(code)
    if not long_url:
        raise HTTPException(status_code=404, detail="Not found")

    # 3️⃣ Populate cache
    redis_client.setex(
        f"code:{code}",
        86400,  # 24 hours
        long_url,
    )

    return {
        "source": "db",
        "long_url": long_url,
    }
