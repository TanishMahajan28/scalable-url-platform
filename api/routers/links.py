from fastapi import APIRouter

router = APIRouter()

@router.post("/links")
async def create_link(payload: dict):
    return {
        "message": "link created",
        "long_url": payload["long_url"],
    }
