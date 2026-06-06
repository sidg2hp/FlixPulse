import os
import pandas as pd
import numpy as np

def main():
    print("Starting data preparation script...")
    raw_dir = "dataset"
    processed_dir = os.path.join("data", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    combined_1_path = os.path.join(raw_dir, "combined_data_1.txt")
    movie_titles_path = os.path.join(raw_dir, "movie_titles.csv")
    
    if not os.path.exists(combined_1_path):
        print(f"Error: {combined_1_path} not found.")
        return
    if not os.path.exists(movie_titles_path):
        print(f"Error: {movie_titles_path} not found.")
        return

    # 1. Parse combined_data_1.txt
    print("Parsing combined_data_1.txt...")
    ratings_data = []
    current_movie_id = None
    
    # Reading file and extracting data
    count = 0
    with open(combined_1_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.endswith(':'):
                current_movie_id = int(line[:-1])
            else:
                parts = line.split(',')
                user_id = int(parts[0])
                rating = int(parts[1])
                date = parts[2]
                ratings_data.append((user_id, current_movie_id, rating, date))
                count += 1
                if count % 5000000 == 0:
                    print(f"Parsed {count} ratings...")

    print(f"Total parsed ratings from file 1: {len(ratings_data)}")

    # Convert to DataFrame
    print("Creating DataFrame...")
    df = pd.DataFrame(ratings_data, columns=['user_id', 'movie_id', 'rating', 'date'])
    ratings_data = None # Free memory

    # 2. Filter to a dense subset
    # Filter users who have rated at least 150 movies
    # Filter movies with at least 1000 ratings
    print("Filtering dense subset...")
    user_counts = df['user_id'].value_counts()
    movie_counts = df['movie_id'].value_counts()
    
    active_users = user_counts[user_counts >= 150].index
    popular_movies = movie_counts[movie_counts >= 1000].index
    
    print(f"Initial: {df['user_id'].nunique()} users, {df['movie_id'].nunique()} movies")
    df_filtered = df[df['user_id'].isin(active_users) & df['movie_id'].isin(popular_movies)]
    print(f"Filtered: {df_filtered['user_id'].nunique()} users, {df_filtered['movie_id'].nunique()} movies, {len(df_filtered)} ratings")

    # Let's write out a subset of size ~500k
    # If filtered set is too large, let's take a sample of it, or keep it if it's around 500k-1M.
    # Actually, let's check size. If it is more than 1M ratings, let's trim it a bit to make it very fast.
    if len(df_filtered) > 1000000:
        print("Trimming to top active users and popular movies...")
        top_users = user_counts[user_counts >= 200].index
        top_movies = movie_counts[movie_counts >= 2000].index
        df_filtered = df[df['user_id'].isin(top_users) & df['movie_id'].isin(top_movies)]
        print(f"Trimmed: {df_filtered['user_id'].nunique()} users, {df_filtered['movie_id'].nunique()} movies, {len(df_filtered)} ratings")

    # Save ratings subset
    ratings_output_path = os.path.join(processed_dir, "ratings_subset.csv")
    df_filtered.to_csv(ratings_output_path, index=False)
    print(f"Saved ratings subset to {ratings_output_path}")

    # 3. Parse movie titles and map to filtered movies
    print("Parsing movie_titles.csv...")
    movies_metadata = []
    with open(movie_titles_path, 'r', encoding='latin1') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',', 2)
            if len(parts) >= 3:
                m_id = int(parts[0])
                year = parts[1]
                title = parts[2]
                movies_metadata.append((m_id, year, title))
            elif len(parts) == 2:
                m_id = int(parts[0])
                year = parts[1]
                movies_metadata.append((m_id, year, "Unknown"))

    df_movies = pd.DataFrame(movies_metadata, columns=['movie_id', 'year', 'title'])
    
    # Filter to only the movies present in our filtered ratings dataset
    unique_movies = df_filtered['movie_id'].unique()
    df_movies_filtered = df_movies[df_movies['movie_id'].isin(unique_movies)]
    
    movies_output_path = os.path.join(processed_dir, "movies_subset.csv")
    df_movies_filtered.to_csv(movies_output_path, index=False)
    print(f"Saved movies subset to {movies_output_path}")
    print("Data preparation complete!")

if __name__ == "__main__":
    main()
