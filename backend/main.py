from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from recommender import RecommenderEngine
import uvicorn

app = FastAPI(title="Netflix Recommender System API", version="1.0")

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production if necessary
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate recommendation engine (this loads pickle files on startup)
engine = RecommenderEngine()

@app.get("/")
def home():
    return {"message": "Netflix Recommendation System API is active. Go to /docs for API documentation."}

@app.get("/api/stats")
def get_stats():
    try:
        return engine.get_dataset_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users")
def get_users(count: int = Query(30, description="Number of sample users to retrieve")):
    try:
        return engine.get_sample_users(count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}/history")
def get_user_history(user_id: int):
    try:
        history = engine.get_user_history(user_id)
        if not history and user_id not in engine.df_ratings["user_id"].values:
            raise HTTPException(status_code=404, detail="User not found in dataset history")
        return history
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}/recommendations")
def get_recommendations(user_id: int, count: int = Query(10, description="Number of recommendations")):
    try:
        return engine.get_recommendations(user_id, k=count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/movies/search")
def search_movies(q: str = Query(None, description="Query string for movie title")):
    if not q:
        return []
    try:
        return engine.search_movies(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/movies/{movie_id}/similar")
def get_similar_movies(movie_id: int, count: int = Query(6, description="Number of similar movies")):
    try:
        similar = engine.get_similar_movies(movie_id, k=count)
        return similar
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
