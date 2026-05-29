from fastapi import APIRouter, Depends, HTTPException
from database import reviews_collection, places_collection, ratings_collection
from routes.auth import get_current_user
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime

router = APIRouter()

class ReviewModel(BaseModel):
    place_id: str
    rating: float
    comment: str

@router.post("")
def add_review(data: ReviewModel, current_user = Depends(get_current_user)):
    if not (1 <= data.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    
    user_id = str(current_user["_id"])
    
    review = {
        "user_id": user_id,
        "user_name": current_user["name"],
        "place_id": data.place_id,
        "rating": data.rating,
        "comment": data.comment,
        "created_at": datetime.utcnow()
    }
    reviews_collection.insert_one(review)
    
    ratings_collection.update_one(
        {"user_id": user_id, "place_id": data.place_id},
        {"$set": {"rating": data.rating, "updated_at": datetime.utcnow()}},
        upsert=True
    )
    
    all_ratings = list(ratings_collection.find({"place_id": data.place_id}))
    avg = sum(r["rating"] for r in all_ratings) / len(all_ratings)
    places_collection.update_one(
        {"_id": ObjectId(data.place_id)},
        {"$set": {"avg_rating": round(avg, 2), "rating_count": len(all_ratings)}}
    )
    
    return {"message": "Review added", "avg_rating": round(avg, 2)}

@router.get("/{place_id}")
def get_reviews(place_id: str):
    reviews = list(reviews_collection.find({"place_id": place_id}).sort("created_at", -1).limit(20))
    for r in reviews:
        r["id"] = str(r["_id"])
        del r["_id"]
    return reviews