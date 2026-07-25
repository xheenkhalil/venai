from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """
    Get the currently authenticated user's JWT payload.
    In a real app, you might look up the user in the database here using the 'sub' claim.
    """
    return {"status": "success", "user": user}
