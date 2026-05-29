from fastapi import APIRouter, Depends
from database import behavior_collection
from routes.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class BehaviorModel(BaseModel):
    place_id: str
    event_type: str  # click, view, wishlist, like, search
    time_spent_sec: int = 0

@router.post("")
def log_behavior(data: BehaviorModel, current_user = Depends(get_current_user)):
    behavior_collection.insert_one({
        "user_id": str(current_user["_id"]),
        "place_id": data.place_id,
        "event_type": data.event_type,
        "time_spent_sec": data.time_spent_sec,
        "created_at": datetime.utcnow()
    })
    return {"logged": True}