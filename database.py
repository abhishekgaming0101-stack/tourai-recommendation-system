from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "touristdb")

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

users_collection = db["users"]
places_collection = db["places"]
reviews_collection = db["reviews"]
ratings_collection = db["ratings"]
behavior_collection = db["behavior"]