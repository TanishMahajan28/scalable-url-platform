from fastapi import FastAPI
from api.routers import links, redirect

app = FastAPI(title="Scalable URL Platform")

@app.get("/healthz")
def health():
    return {"status": "ok"}

app.include_router(links.router, prefix="/v1")
app.include_router(redirect.router)
