from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, places, recommendations, reviews, behavior, admin

app = FastAPI(title="Tourist Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(places.router, prefix="/api/places", tags=["Places"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(behavior.router, prefix="/api/behavior", tags=["Behavior"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.get("/")
def root():
    return {"message": "Tourist Recommendation API running"}