from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from hybrid import HybridEngine
from database import db
from bson import ObjectId

app = FastAPI(title="ML Recommendation Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = HybridEngine()

def load_and_train():
    places_raw = list(db["places"].find({}))
    places = []
    for p in places_raw:
        p["id"] = str(p["_id"])
        del p["_id"]
        places.append(p)
    
    engine.cbf.fit(places)
    
    ratings_raw = list(db["ratings"].find({}))
    if ratings_raw:
        ratings = [{"user_id": r["user_id"], "place_id": r["place_id"], "rating": r["rating"]} for r in ratings_raw]
        engine.cf.fit(ratings)
    
    print(f"✅ Models trained: {len(places)} places, {len(ratings_raw)} ratings")
    return places

ALL_PLACES = load_and_train()

class RecommendRequest(BaseModel):
    user_id: str
    user_profile: dict

@app.post("/recommend")
def recommend(data: RecommendRequest):
    global ALL_PLACES
    ALL_PLACES = load_and_train()
    
    user_ratings = list(db["ratings"].find({"user_id": data.user_id}))
    rated_ids = [r["place_id"] for r in user_ratings]
    rating_count = len(user_ratings)
    
    all_place_ids = [p["id"] for p in ALL_PLACES]
    
    recommendations = engine.recommend(
        user_id=data.user_id,
        user_profile=data.user_profile,
        rating_count=rating_count,
        all_place_ids=all_place_ids,
        rated_place_ids=rated_ids,
        top_n=10
    )
    
    result = []
    for rec in recommendations:
        place = db["places"].find_one({"_id": ObjectId(rec["place_id"])})
        if place:
            place["id"] = str(place["_id"])
            del place["_id"]
            place["recommendation_info"] = {
                "hybrid_score": rec["hybrid_score"],
                "method": rec["method"],
                "alpha": rec["alpha"],
                "beta": rec["beta"]
            }
            result.append(place)
    
    return result

@app.get("/similar/{place_id}")
def similar(place_id: str):
    global ALL_PLACES
    if not engine.cbf.fitted:
        ALL_PLACES = load_and_train()
    
    similar_list = engine.cbf.get_similar(place_id, top_n=6)
    
    result = []
    for s in similar_list:
        place = db["places"].find_one({"_id": ObjectId(s["place_id"])})
        if place:
            place["id"] = str(place["_id"])
            del place["_id"]
            place["similarity_score"] = s["score"]
            result.append(place)
    return result

@app.get("/trending")
def trending():
    places = list(db["places"].find({}).sort("avg_rating", -1).limit(8))
    for p in places:
        p["id"] = str(p["_id"])
        del p["_id"]
    return places

@app.post("/retrain")
def retrain():
    global ALL_PLACES
    ALL_PLACES = load_and_train()
    return {"message": "Models retrained successfully", "places": len(ALL_PLACES)}