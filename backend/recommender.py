import os
import pickle
import pandas as pd
import numpy as np

class RecommenderEngine:
    def __init__(self):
        self.models_dir = os.path.join(os.path.dirname(__file__), "models")
        self.ratings_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "ratings_subset.csv")
        
        print("Loading models and metadata...")
        # Load SVD Model
        with open(os.path.join(self.models_dir, "svd_model.pkl"), "rb") as f:
            self.svd_model = pickle.load(f)
            
        # Load KNN Model
        with open(os.path.join(self.models_dir, "knn_model.pkl"), "rb") as f:
            self.knn_model = pickle.load(f)
            
        # Load Movies Meta
        with open(os.path.join(self.models_dir, "movies_meta.pkl"), "rb") as f:
            self.df_movies = pickle.load(f)
            
        # Load Ratings subset
        self.df_ratings = pd.read_csv(self.ratings_path)
        
        # Cache list of unique movie IDs
        self.all_movie_ids = self.df_movies["movie_id"].unique()
        
        print("Recommender engine loaded successfully!")

    def get_sample_users(self, count=30):
        """Get top active users to display in the dropdown selection on the frontend."""
        user_counts = self.df_ratings["user_id"].value_counts().head(count)
        users = []
        for u_id, num_ratings in user_counts.items():
            # Get average rating of this user
            avg_rating = self.df_ratings[self.df_ratings["user_id"] == u_id]["rating"].mean()
            users.append({
                "user_id": int(u_id),
                "ratings_count": int(num_ratings),
                "avg_rating": float(round(avg_rating, 2))
            })
        return users

    def get_user_history(self, user_id):
        """Retrieve ratings history for a user mapped to movie titles."""
        user_history = self.df_ratings[self.df_ratings["user_id"] == user_id]
        if user_history.empty:
            return []
            
        merged = user_history.merge(self.df_movies, on="movie_id")
        merged = merged.sort_values(by="rating", ascending=False)
        
        history = []
        for _, row in merged.iterrows():
            history.append({
                "movie_id": int(row["movie_id"]),
                "title": str(row["title"]),
                "year": str(row["year"]),
                "rating": float(row["rating"]),
                "date": str(row["date"])
            })
        return history

    def get_recommendations(self, user_id, k=10):
        """Generate Top-K recommendations using SVD (with fallback for cold-start)."""
        # Check if user exists in training dataset
        user_exists = user_id in self.df_ratings["user_id"].values
        
        if not user_exists:
            # Cold-start user strategy: return popular high-rated items
            print(f"Cold start strategy for user {user_id}")
            return self.get_popularity_recommendations(k)
            
        # User exists, get rated movies
        rated_movie_ids = self.df_ratings[self.df_ratings["user_id"] == user_id]["movie_id"].values
        
        # Identify unrated movies
        unrated_movie_ids = [m_id for m_id in self.all_movie_ids if m_id not in rated_movie_ids]
        
        # Predict ratings
        predictions = []
        for m_id in unrated_movie_ids:
            pred = self.svd_model.predict(user_id, m_id)
            predictions.append((m_id, pred.est))
            
        # Sort by predicted score
        predictions.sort(key=lambda x: x[1], reverse=True)
        top_k = predictions[:k]
        
        # Merge with movie metadata
        recs = []
        for m_id, est_score in top_k:
            movie_info = self.df_movies[self.df_movies["movie_id"] == m_id]
            if not movie_info.empty:
                title = movie_info["title"].values[0]
                year = movie_info["year"].values[0]
                recs.append({
                    "movie_id": int(m_id),
                    "title": str(title),
                    "year": str(year),
                    "predicted_rating": float(round(est_score, 2)),
                    "explanation": self.get_explanation(user_id, m_id)
                })
        return recs

    def get_popularity_recommendations(self, k=10):
        """Return most popular items (highest mean rating for items with many ratings)."""
        movie_stats = self.df_ratings.groupby("movie_id")["rating"].agg(["count", "mean"])
        popular_movies = movie_stats[movie_stats["count"] >= 2000]
        top_popular = popular_movies.sort_values(by="mean", ascending=False).head(k)
        
        recs = []
        for m_id, row in top_popular.iterrows():
            movie_info = self.df_movies[self.df_movies["movie_id"] == m_id]
            title = movie_info["title"].values[0] if not movie_info.empty else "Unknown"
            year = movie_info["year"].values[0] if not movie_info.empty else "Unknown"
            recs.append({
                "movie_id": int(m_id),
                "title": str(title),
                "year": str(year),
                "predicted_rating": float(round(row["mean"], 2)),
                "explanation": "Recommended because it is highly rated by many users (Cold Start fallback)."
            })
        return recs

    def get_explanation(self, user_id, rec_movie_id):
        """Generate an item-based similarity explanation for why a movie is recommended."""
        # Get user's high-rated movies in history (rating >= 4)
        user_history = self.df_ratings[(self.df_ratings["user_id"] == user_id) & (self.df_ratings["rating"] >= 4.0)]
        if user_history.empty:
            return "Recommended because it aligns with popular preferences in your region."
            
        try:
            # Map recommended movie ID to KNN inner ID
            rec_inner_id = self.knn_model.trainset.to_inner_iid(rec_movie_id)
        except ValueError:
            return "Recommended based on overall system popularity."
            
        similarities = []
        for _, row in user_history.iterrows():
            hist_movie_id = int(row["movie_id"])
            rating = row["rating"]
            try:
                hist_inner_id = self.knn_model.trainset.to_inner_iid(hist_movie_id)
                sim = self.knn_model.sim[rec_inner_id, hist_inner_id]
                similarities.append((hist_movie_id, sim, rating))
            except ValueError:
                continue
                
        if not similarities:
            return "Recommended based on overall system popularity."
            
        # Get highest similarity match
        similarities.sort(key=lambda x: x[1], reverse=True)
        similar_movie_id, sim_score, rating = similarities[0]
        
        # If similarity is too low, return general message
        if sim_score <= 0.05:
            return "Recommended because it matches your overall movie profile."
            
        watched_info = self.df_movies[self.df_movies["movie_id"] == similar_movie_id]
        watched_title = watched_info["title"].values[0] if not watched_info.empty else "another movie"
        
        return (
            f"Because you gave '{watched_title}' a high rating of {int(rating)} "
            f"(Similarity: {sim_score*100:.0f}%)"
        )

    def get_similar_movies(self, movie_id, k=6):
        """Retrieve similar movies based on KNN model items similarity weights."""
        try:
            inner_id = self.knn_model.trainset.to_inner_iid(movie_id)
        except ValueError:
            return []
            
        # Get neighbors
        neighbors = self.knn_model.get_neighbors(inner_id, k=k)
        
        similar_movies = []
        for inner_neigh in neighbors:
            neigh_movie_id = self.knn_model.trainset.to_raw_iid(inner_neigh)
            sim_score = self.knn_model.sim[inner_id, inner_neigh]
            movie_info = self.df_movies[self.df_movies["movie_id"] == neigh_movie_id]
            if not movie_info.empty:
                similar_movies.append({
                    "movie_id": int(neigh_movie_id),
                    "title": str(movie_info["title"].values[0]),
                    "year": str(movie_info["year"].values[0]),
                    "similarity": float(round(sim_score, 3))
                })
        return similar_movies

    def search_movies(self, query, count=10):
        """Search movies subset by title."""
        if not query:
            return []
        matches = self.df_movies[self.df_movies["title"].str.contains(query, case=False, na=False)].head(count)
        results = []
        for _, row in matches.iterrows():
            results.append({
                "movie_id": int(row["movie_id"]),
                "title": str(row["title"]),
                "year": str(row["year"])
            })
        return results

    def get_dataset_stats(self):
        """Generate metrics for the interactive analytics dashboard."""
        n_ratings = len(self.df_ratings)
        n_users = self.df_ratings["user_id"].nunique()
        n_movies = self.df_ratings["movie_id"].nunique()
        sparsity = (1 - (n_ratings / (n_users * n_movies))) * 100
        mean_rating = self.df_ratings["rating"].mean()
        
        # Rating counts
        rating_counts = self.df_ratings["rating"].value_counts().sort_index().to_dict()
        
        # Top movies by popularity
        movie_stats = self.df_ratings.groupby("movie_id")["rating"].agg(["count", "mean"]).reset_index()
        top_rated = movie_stats[movie_stats["count"] >= 1000].sort_values(by="mean", ascending=False).head(5)
        top_rated_merged = top_rated.merge(self.df_movies, on="movie_id")
        
        top_movies = []
        for _, row in top_rated_merged.iterrows():
            top_movies.append({
                "title": str(row["title"]),
                "avg_rating": float(round(row["mean"], 2)),
                "ratings_count": int(row["count"])
            })
            
        return {
            "total_ratings": n_ratings,
            "total_users": n_users,
            "total_movies": n_movies,
            "sparsity": float(round(sparsity, 2)),
            "avg_rating": float(round(mean_rating, 2)),
            "rating_distribution": {str(k): int(v) for k, v in rating_counts.items()},
            "top_movies": top_movies,
            "models_performance": [
                {
                    "model": "SVD (Matrix Factorization)",
                    "rmse": 0.8160,
                    "map_10": 0.7427,
                    "train_time_sec": 8.92
                },
                {
                    "model": "KNN (Item-Based CF)",
                    "rmse": 0.8553,
                    "map_10": 0.7079,
                    "train_time_sec": 225.86
                }
            ]
        }
