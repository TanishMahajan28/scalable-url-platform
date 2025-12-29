import redis
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from shared.redis import eval_rate_limit

RATE_LIMIT = 5
WINDOW_SECONDS = 60
COST = 1

REFILL_RATE = RATE_LIMIT / WINDOW_SECONDS


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        key = f"tb:{client_ip}"

        try:
            allowed, remaining, retry_after = eval_rate_limit(
                key=key,
                capacity=RATE_LIMIT,
                refill_rate=REFILL_RATE,
                cost=COST,
            )

            allowed = int(allowed)
            remaining = int(float(remaining))
            retry_after = int(retry_after)

            if allowed == 0:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"},
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(RATE_LIMIT),
                        "X-RateLimit-Remaining": str(max(0, remaining)),
                    },
                )

        except redis.RedisError as e:
            # FAIL OPEN — never block traffic if Redis is down
            print("REDIS ERROR (token bucket):", repr(e))
            return await call_next(request)

        return await call_next(request)
