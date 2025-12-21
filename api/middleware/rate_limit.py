import time
import redis
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from shared.redis import redis_client

RATE_LIMIT = 5
WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_window = int(time.time() // WINDOW_SECONDS)
        key = f"rate:{client_ip}:{current_window}"

        try:
            current_count = redis_client.incr(key)

            if current_count == 1:
                redis_client.expire(key, WINDOW_SECONDS)

            if current_count > RATE_LIMIT:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"},
                    headers={
                        "Retry-After": str(WINDOW_SECONDS),
                        "X-RateLimit-Limit": str(RATE_LIMIT),
                        "X-RateLimit-Remaining": "0",
                    },
                )

        except redis.RedisError as e:
            print("REDIS ERROR in rate limiter:", repr(e))
            # Fail open
            return await call_next(request)

        return await call_next(request)
