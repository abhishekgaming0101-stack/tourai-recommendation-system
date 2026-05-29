from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from database import users_collection
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey123tourist")

class RegisterModel(BaseModel):
    name: str
    email: str
    password: str
    preferred_categories: list = []
    budget: str = "medium"
    travel_type: str = "solo"

class LoginModel(BaseModel):
    email: str
    password: str

def create_token(user_id: str, email: str):
    data = {"sub": user_id, "email": email, "exp": datetime.utcnow() + timedelta(days=7)}
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_admin_user(current_user = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.post("/register")
def register(data: RegisterModel):
    if users_collection.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = {
        "name": data.name,
        "email": data.email,
        "password": pwd_context.hash(data.password),
        "role": "user",
        "preferred_categories": data.preferred_categories,
        "budget": data.budget,
        "travel_type": data.travel_type,
        "wishlist": [],
        "liked_places": [],
        "created_at": datetime.utcnow()
    }
    result = users_collection.insert_one(user)
    token = create_token(str(result.inserted_id), data.email)
    return {"token": token, "name": data.name, "email": data.email, "id": str(result.inserted_id)}

@router.post("/login")
def login(data: LoginModel):
    user = users_collection.find_one({"email": data.email})
    if not user or not pwd_context.verify(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(str(user["_id"]), user["email"])
    return {
        "token": token,
        "name": user["name"],
        "email": user["email"],
        "id": str(user["_id"]),
        "preferred_categories": user.get("preferred_categories", []),
        "role": user.get("role", "user")
    }

@router.get("/me")
def get_me(current_user = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "name": current_user["name"],
        "email": current_user["email"],
        "preferred_categories": current_user.get("preferred_categories", []),
        "budget": current_user.get("budget", "medium"),
        "travel_type": current_user.get("travel_type", "solo"),
        "wishlist": current_user.get("wishlist", []),
        "liked_places": current_user.get("liked_places", []),
        "role": current_user.get("role", "user")
    }

@router.put("/profile")
def update_profile(data: dict, current_user = Depends(get_current_user)):
    users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": {
            "preferred_categories": data.get("preferred_categories", []),
            "budget": data.get("budget", "medium"),
            "travel_type": data.get("travel_type", "solo")
        }}
    )
    return {"message": "Profile updated"}