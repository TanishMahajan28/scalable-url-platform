import pathlib
import time
import redis
from api.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
)

# Load Lua script text only (no Redis calls here)
_lua_path = pathlib.Path(__file__).with_name("ratelimit.lua")
RATE_LIMIT_LUA = _lua_path.read_text()


def now_ms() -> int:
    return int(time.time() * 1000)


def eval_rate_limit(key: str, capacity: int, refill_rate: float, cost: int):
    """
    Safely evaluate token bucket Lua script.
    Handles NOSCRIPT and Redis restarts.
    """
    try:
        return redis_client.eval(
            RATE_LIMIT_LUA,
            1,
            key,
            str(capacity),
            str(refill_rate),
            str(now_ms()),
            str(cost),
        )
    except redis.exceptions.ConnectionError:
        raise
