# Slides Outline: Personalized Movie Discovery System

This presentation outline covers the **8 Slides** requested for the Cult Open Projects 2026 AI/ML Presentation deliverable.

---

## Slide 1: Title & Project Overview
* **Slide Title**: FlixPulse: Latent Factor Movie Recommendation & Analytics
* **Sub-title**: Personalized Movie Discovery Engine using the Netflix Prize Dataset
* **Content**:
  - **Goal**: Develop an end-to-end personalization system using matrix factorization and neighborhood filtering.
  - **Key Outcomes**: Personalized discovery, explainable recommendations, dynamic cold-start strategy, and full-stack interactive dashboard.

---

## Slide 2: Problem Definition & Sparsity
* **Slide Title**: The Personalization Challenge: Sparsity & Cold-Start
* **Content**:
  - **Data Sparsity**: Real-world user logs are extremely sparse (>99% unrated).
  - **Inference Latency**: Real-time services must resolve recommendations in milliseconds.
  - **Cold-Start**: Managing predictions for users or movies with zero historical ratings.
  - **Explainability Gap**: Machine learning predictions are often "black boxes" that users do not trust.

---

## Slide 3: Dataset Features & EDA Highlights
* **Slide Title**: Netflix Subset Insights & User Statistics
* **Content**:
  - **Dense Core Subset**: 21,045 active users, 1,287 movies, and 5.7M ratings.
  - **Rating Skewness**: Over 60% of ratings are 4★ or 5★, giving a mean rating of 3.73 (positive selection bias).
  - **Sparsity Characteristic**: Density is 21.04% (matrix is 78.96% sparse).
  - **Long Tail Distribution**: Blockbuster titles capture a disproportionate share of reviews.

---

## Slide 4: Model Architectures
* **Slide Title**: SVD Latent Factors & KNN Neighborhood Models
* **Content**:
  - **Matrix Factorization (SVD)**:
    - Learns latent user vectors $p_u$ and item vectors $q_i$.
    - Predicts ratings as $\hat{r}_{u,i} = \mu + b_u + b_i + p_u^T q_i$.
    - Optimized using Stochastic Gradient Descent (SGD).
  - **Item-Based Neighborhood Model (KNN)**:
    - Calculates movie similarities using adjusted Cosine Correlation.
    - Predicts ratings based on weighted average of nearest rated items.

---

## Slide 5: Model Evaluation & Metric Comparison
* **Slide Title**: RMSE Prediction vs. MAP@10 Ranking Performance
* **Content**:
  - **Split Validation**: 80-20 Train-Test split.
  - **Evaluation Metrics**:
    - **RMSE**: Rating accuracy (lower is better).
    - **MAP@10**: Ranking quality for Top-10 lists (higher is better).
  - **Results Table**:
    - **SVD**: RMSE = **0.8160**, MAP@10 = **0.7427** (Train Time: **8.92s**)
    - **KNN**: RMSE = `0.8553`, MAP@10 = `0.7079` (Train Time: `225.86s`)

---

## Slide 6: Explainable Recommendation Engine
* **Slide Title**: Explainable AI: Combining SVD Accuracy with KNN Interpretability
* **Content**:
  - **The Trade-off**: SVD is highly accurate but uninterpretable. KNN is explainable but less accurate.
  - **Hybrid Solution**: SVD generates recommendations, while KNN similarity weights generate explanations.
  - **Example Explanation**:
    - *"Because you gave 'Toy Story' a 5 (Similarity: 98%), we recommend 'Toy Story 2' (SVD score: 4.8★)"*

---

## Slide 7: Cold Start & Mitigation
* **Slide Title**: Handling Cold-Start for Users and Movies
* **Content**:
  - **New User Strategy**: Fallback to popularity recommender (returning movies with highest mean rating among those with $\ge 2000$ ratings).
  - **New Movie Strategy**:
    - Use genre metadata overlaps to match similarity metrics.
    - Implement $\epsilon$-greedy exploration to inject new releases to active user feeds.
  - **Sparse History Strategy**: Populate initial feeds with a mixture of popularity averages and hybrid item-based predictions.

---

## Slide 8: Deployment Architecture & Future Scope
* **Slide Title**: Decoupled Web Application & Interactive Dashboard
* **Content**:
  - **Backend**: FastAPI REST server providing fast, cached recommendations and similarity searches.
  - **Frontend**: Vite-based React SPA with premium dark-mode glassmorphism styling and custom SVG stats charts.
  - **Future Scope**:
    - Incorporate deep neural collaborative networks.
    - Integrate scraping scripts for TMDB movie posters and trailers.
