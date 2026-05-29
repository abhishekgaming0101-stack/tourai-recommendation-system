from fastapi import APIRouter, Depends
from routes.auth import get_current_user
import httpx

router = APIRouter()
ML_URL = "http://localhost:8001"

@router.get("")
async def get_recommendations(current_user = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    user_profile = {
        "preferred_categories": current_user.get("preferred_categories", []),
        "budget": current_user.get("budget", "medium"),
        "liked_places": current_user.get("liked_places", []),
        "wishlist": current_user.get("wishlist", [])
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f"{ML_URL}/recommend", json={
            "user_id": user_id,
            "user_profile": user_profile
        })
    return response.json()

@router.get("/trending")
async def get_trending():
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(f"{ML_URL}/trending")
    return response.json()

@router.get("/similar/{place_id}")
async def get_similar(place_id: str):
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(f"{ML_URL}/similar/{place_id}")
    return response.json()