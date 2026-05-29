from fastapi import APIRouter, HTTPException, Depends, Query
from database import places_collection, users_collection
from routes.auth import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter()

def place_to_dict(p):
    p["id"] = str(p["_id"])
    del p["_id"]
    return p

@router.get("")
def get_places(
    category: str = None,
    budget: str = None,
    state: str = None,
    search: str = None,
    page: int = 1,
    limit: int = 12
):
    query = {}
    if category:
        query["category"] = category
    if budget:
        query["budget"] = budget
    if state:
        query["state"] = {"$regex": state, "$options": "i"}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"tags": {"$in": [search.lower()]}}
        ]
    
    skip = (page - 1) * limit
    places = list(places_collection.find(query).skip(skip).limit(limit))
    return [place_to_dict(p) for p in places]

@router.get("/user/wishlist")
def get_wishlist(current_user = Depends(get_current_user)):
    wishlist_ids = current_user.get("wishlist", [])
    places = []
    for pid in wishlist_ids:
        try:
            p = places_collection.find_one({"_id": ObjectId(pid)})
            if p:
                places.append(place_to_dict(p))
        except:
            pass
    return places

@router.get("/{place_id}")
def get_place(place_id: str):
    place = places_collection.find_one({"_id": ObjectId(place_id)})
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place_to_dict(place)

@router.post("/wishlist/{place_id}")
def toggle_wishlist(place_id: str, current_user = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    wishlist = current_user.get("wishlist", [])
    
    if place_id in wishlist:
        users_collection.update_one({"_id": current_user["_id"]}, {"$pull": {"wishlist": place_id}})
        return {"message": "Removed from wishlist", "in_wishlist": False}
    else:
        users_collection.update_one({"_id": current_user["_id"]}, {"$push": {"wishlist": place_id}})
        return {"message": "Added to wishlist", "in_wishlist": True}

@router.post("/like/{place_id}")
def toggle_like(place_id: str, current_user = Depends(get_current_user)):
    liked = current_user.get("liked_places", [])
    if place_id in liked:
        users_collection.update_one({"_id": current_user["_id"]}, {"$pull": {"liked_places": place_id}})
        return {"liked": False}
    else:
        users_collection.update_one({"_id": current_user["_id"]}, {"$push": {"liked_places": place_id}})
        return {"liked": True}