from fastapi import APIRouter

router = APIRouter()

@router.get("/{code}")
async def redirect(code: str):
    return {"code": code}
