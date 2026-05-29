from fastapi import APIRouter, Depends, HTTPException
from database import places_collection, users_collection, reviews_collection, ratings_collection, behavior_collection
from routes.auth import get_admin_user
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from passlib.context import CryptContext


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def place_to_dict(p):
    p["id"] = str(p["_id"])
    del p["_id"]
    return p

class PlaceModel(BaseModel):
    name: str
    state: str
    city: str
    category: str
    description: str
    tags: List[str] = []
    budget: str = "medium"
    best_season: str = "winter"
    lat: float = 0.0
    lng: float = 0.0
    image: str = ""

@router.get("/stats")
def get_stats(admin = Depends(get_admin_user)):
    total_users = users_collection.count_documents({})
    total_places = places_collection.count_documents({})
    total_reviews = reviews_collection.count_documents({})
    total_behaviors = behavior_collection.count_documents({})
    
    recent_users = list(users_collection.find({}, {"password": 0}).sort("created_at", -1).limit(5))
    for u in recent_users:
        u["id"] = str(u["_id"])
        del u["_id"]
    
    category_stats = {}
    for cat in ["heritage", "beach", "nature", "wildlife", "hill", "adventure", "religious"]:
        category_stats[cat] = places_collection.count_documents({"category": cat})
    
    return {
        "total_users": total_users,
        "total_places": total_places,
        "total_reviews": total_reviews,
        "total_behaviors": total_behaviors,
        "recent_users": recent_users,
        "category_stats": category_stats
    }

@router.get("/users")
def get_all_users(admin = Depends(get_admin_user)):
    users = list(users_collection.find({}, {"password": 0}).sort("created_at", -1))
    for u in users:
        u["id"] = str(u["_id"])
        del u["_id"]
    return users

@router.delete("/users/{user_id}")
def delete_user(user_id: str, admin = Depends(get_admin_user)):
    result = users_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}

@router.get("/places")
def get_all_places(admin = Depends(get_admin_user)):
    places = list(places_collection.find({}).sort("name", 1))
    return [place_to_dict(p) for p in places]

@router.post("/places")
def add_place(data: PlaceModel, admin = Depends(get_admin_user)):
    place = data.dict()
    place["avg_rating"] = 0.0
    place["rating_count"] = 0
    place["created_at"] = datetime.utcnow()
    if not place["image"]:
        place["image"] = "/places/taj-mahal.jpg"
    place["images"] = [place["image"]]
    result = places_collection.insert_one(place)
    return {"message": "Place added", "id": str(result.inserted_id)}

@router.delete("/places/{place_id}")
def delete_place(place_id: str, admin = Depends(get_admin_user)):
    result = places_collection.delete_one({"_id": ObjectId(place_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Place not found")
    reviews_collection.delete_many({"place_id": place_id})
    ratings_collection.delete_many({"place_id": place_id})
    return {"message": "Place deleted"}

@router.get("/reviews")
def get_all_reviews(admin = Depends(get_admin_user)):
    reviews = list(reviews_collection.find({}).sort("created_at", -1))
    for r in reviews:
        r["id"] = str(r["_id"])
        del r["_id"]
    return reviews

@router.delete("/reviews/{review_id}")
def delete_review(review_id: str, admin = Depends(get_admin_user)):
    review = reviews_collection.find_one({"_id": ObjectId(review_id)})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    reviews_collection.delete_one({"_id": ObjectId(review_id)})
    all_ratings = list(ratings_collection.find({"place_id": review["place_id"]}))
    if all_ratings:
        avg = sum(r["rating"] for r in all_ratings) / len(all_ratings)
        places_collection.update_one(
            {"_id": ObjectId(review["place_id"])},
            {"$set": {"avg_rating": round(avg, 2), "rating_count": len(all_ratings)}}
        )
    return {"message": "Review deleted"}

@router.get("/cf-analysis")
def get_cf_analysis(admin = Depends(get_admin_user)):
    import math

    # Get all ratings
    all_ratings = list(ratings_collection.find({}))
    if len(all_ratings) < 2:
        return {"users": [], "pairs": []}

    # Group ratings by user
    user_ratings = {}
    for r in all_ratings:
        uid = r["user_id"]
        if uid not in user_ratings:
            user_ratings[uid] = {}
        user_ratings[uid][r["place_id"]] = r["rating"]

    # Get user details
    users = {}
    for uid in user_ratings:
        try:
            u = users_collection.find_one({"_id": ObjectId(uid)})
            if u:
                users[uid] = {
                    "id": uid,
                    "name": u.get("name", "Unknown"),
                    "email": u.get("email", ""),
                    "rating_count": len(user_ratings[uid])
                }
        except Exception:
            pass

    def cosine_similarity(r1, r2):
        common = set(r1.keys()) & set(r2.keys())
        if not common:
            return 0.0
        dot = sum(r1[p] * r2[p] for p in common)
        mag1 = math.sqrt(sum(v**2 for v in r1.values()))
        mag2 = math.sqrt(sum(v**2 for v in r2.values()))
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return round(dot / (mag1 * mag2), 4)

    def pearson_similarity(r1, r2):
        common = set(r1.keys()) & set(r2.keys())
        if len(common) < 2:
            return 0.0
        mean1 = sum(r1[p] for p in common) / len(common)
        mean2 = sum(r2[p] for p in common) / len(common)
        num = sum((r1[p] - mean1) * (r2[p] - mean2) for p in common)
        den1 = math.sqrt(sum((r1[p] - mean1)**2 for p in common))
        den2 = math.sqrt(sum((r2[p] - mean2)**2 for p in common))
        if den1 == 0 or den2 == 0:
            return 0.0
        return round(num / (den1 * den2), 4)

    # Build pairs
    user_ids = list(user_ratings.keys())
    pairs = []

    for i in range(len(user_ids)):
        for j in range(i + 1, len(user_ids)):
            u1 = user_ids[i]
            u2 = user_ids[j]
            if u1 not in users or u2 not in users:
                continue

            r1 = user_ratings[u1]
            r2 = user_ratings[u2]
            common_places = list(set(r1.keys()) & set(r2.keys()))

            cosine = cosine_similarity(r1, r2)
            pearson = pearson_similarity(r1, r2)

            u2_only = {p: r2[p] for p in r2 if p not in r1}
            u1_only = {p: r1[p] for p in r1 if p not in r2}

            # Get place details for common places
            common_details = []
            for pid in common_places[:5]:
                try:
                    place = places_collection.find_one({"_id": ObjectId(pid)})
                    if place:
                        common_details.append({
                            "id": pid,
                            "name": place.get("name", ""),
                            "image": place.get("image", ""),
                            "u1_rating": r1[pid],
                            "u2_rating": r2[pid],
                            "category": place.get("category", "")
                        })
                except Exception:
                    pass

            # Get recommendations from u2 to u1
            recs_u2_to_u1 = []
            for pid, rating in sorted(u2_only.items(), key=lambda x: -x[1])[:5]:
                try:
                    place = places_collection.find_one({"_id": ObjectId(pid)})
                    if place:
                        recs_u2_to_u1.append({
                            "id": pid,
                            "name": place.get("name", ""),
                            "image": place.get("image", ""),
                            "u2_rating": rating,
                            "category": place.get("category", ""),
                            "why": "User " + users[u2]["name"] + " rated this " + str(rating) + "★"
                        })
                except Exception:
                    pass

            # Get recommendations from u1 to u2
            recs_u1_to_u2 = []
            for pid, rating in sorted(u1_only.items(), key=lambda x: -x[1])[:5]:
                try:
                    place = places_collection.find_one({"_id": ObjectId(pid)})
                    if place:
                        recs_u1_to_u2.append({
                            "id": pid,
                            "name": place.get("name", ""),
                            "image": place.get("image", ""),
                            "u1_rating": rating,
                            "category": place.get("category", ""),
                            "why": "User " + users[u1]["name"] + " rated this " + str(rating) + "★"
                        })
                except Exception:
                    pass

            pairs.append({
                "user1": users[u1],
                "user2": users[u2],
                "cosine_similarity": cosine,
                "pearson_similarity": pearson,
                "common_places_count": len(common_places),
                "common_places": common_details,
                "recs_u2_to_u1": recs_u2_to_u1,
                "recs_u1_to_u2": recs_u1_to_u2,
                "similarity_level": "High" if cosine > 0.7 else "Medium" if cosine > 0.4 else "Low"
            })

    # Sort by similarity descending
    pairs.sort(key=lambda x: -x["cosine_similarity"])

    return {
        "users": list(users.values()),
        "pairs": pairs[:20]  # top 20 most similar pairs
    }