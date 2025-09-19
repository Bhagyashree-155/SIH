from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_knowledge_base():
    return {"message": "Knowledge base endpoint - coming soon"}
