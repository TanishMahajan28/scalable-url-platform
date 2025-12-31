from fastapi import FastAPI
from api.middleware.rate_limit import RateLimitMiddleware
from api.routers import links, redirect

app = FastAPI(title="Scalable URL Platform")

# Register rate limiting FIRST
app.add_middleware(RateLimitMiddleware)

@app.get("/healthz")
def health():
    return {"status": "ok"}

app.include_router(links.router, prefix="/v1")
app.include_router(redirect.router)
