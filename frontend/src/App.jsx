import React, { useState, useEffect } from 'react';
import { 
  Tv, 
  Users, 
  Sparkles, 
  BarChart3, 
  Search, 
  Film, 
  TrendingUp, 
  UserCheck, 
  History, 
  ChevronRight, 
  Info,
  Clock,
  Layers,
  Database
} from 'lucide-react';
import './App.css';

const BACKEND_URL = "http://127.0.0.1:8000";

function App() {
  const [activeTab, setActiveTab] = useState('recommendations');
  const [users, setUsers] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [userHistory, setUserHistory] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [stats, setStats] = useState(null);
  
  // Search & Similar movies states
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [similarMovies, setSimilarMovies] = useState([]);
  
  // General UI States
  const [loading, setLoading] = useState(false);
  const [recLoading, setRecLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [similarLoading, setSimilarLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch initial users and stats
  useEffect(() => {
    async function initData() {
      setLoading(true);
      try {
        // Fetch sample users
        const usersRes = await fetch(`${BACKEND_URL}/api/users?count=25`);
        if (!usersRes.ok) throw new Error("Failed to load sample users");
        const usersData = await usersRes.json();
        setUsers(usersData);
        if (usersData.length > 0) {
          setSelectedUserId(usersData[0].user_id);
        }

        // Fetch global stats
        const statsRes = await fetch(`${BACKEND_URL}/api/stats`);
        if (!statsRes.ok) throw new Error("Failed to load statistics");
        const statsData = await statsRes.json();
        setStats(statsData);
      } catch (err) {
        console.error(err);
        setError("Could not connect to FastAPI server. Make sure the backend is running on port 8000.");
      } finally {
        setLoading(false);
      }
    }
    initData();
  }, []);

  // Fetch recommendations and history when selected user changes
  useEffect(() => {
    if (!selectedUserId) return;
    
    async function fetchUserDetails() {
      setRecLoading(true);
      try {
        // Fetch recommendations
        const recsRes = await fetch(`${BACKEND_URL}/api/users/${selectedUserId}/recommendations?count=8`);
        if (!recsRes.ok) throw new Error("Failed to fetch recommendations");
        const recsData = await recsRes.json();
        setRecommendations(recsData);

        // Fetch user history
        const historyRes = await fetch(`${BACKEND_URL}/api/users/${selectedUserId}/history`);
        if (!historyRes.ok) throw new Error("Failed to fetch user history");
        const historyData = await historyRes.json();
        setUserHistory(historyData);
      } catch (err) {
        console.error(err);
        setError("Error loading details for user " + selectedUserId);
      } finally {
        setRecLoading(false);
      }
    }
    fetchUserDetails();
  }, [selectedUserId]);

  // Handle movie search
  const handleSearch = async (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }
    setSearchLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/movies/search?q=${encodeURIComponent(query)}`);
      if (res.ok) {
        const data = await res.json();
        setSearchResults(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSearchLoading(false);
    }
  };

  // Fetch similar movies
  const selectMovieForSimilarity = async (movie) => {
    setSelectedMovie(movie);
    setSimilarLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/movies/${movie.movie_id}/similar?count=6`);
      if (!res.ok) throw new Error("Failed to load similar movies");
      const data = await res.json();
      setSimilarMovies(data);
    } catch (err) {
      console.error(err);
    } finally {
      setSimilarLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Loading Recommender Models and Datasets...</p>
      </div>
    );
  }

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar glass-panel">
        <div className="sidebar-brand">
          <Tv className="brand-icon" />
          <h2>FlixPulse</h2>
        </div>
        <nav className="sidebar-menu">
          <button 
            className={`nav-item ${activeTab === 'recommendations' ? 'active' : ''}`}
            onClick={() => setActiveTab('recommendations')}
          >
            <Sparkles size={18} />
            <span>Discover</span>
          </button>
          <button 
            className={`nav-item ${activeTab === 'explorer' ? 'active' : ''}`}
            onClick={() => setActiveTab('explorer')}
          >
            <Search size={18} />
            <span>Similarity Explorer</span>
          </button>
          <button 
            className={`nav-item ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            <BarChart3 size={18} />
            <span>Dashboard Stats</span>
          </button>
        </nav>
        {stats && (
          <div className="sidebar-footer">
            <div className="dataset-badge">
              <Database size={14} />
              <span>Netflix Subset</span>
            </div>
            <p>{stats.total_ratings.toLocaleString()} ratings</p>
          </div>
        )}
      </aside>

      {/* Main Content Area */}
      <main className="content-area animate-fade-in">
        {error && (
          <div className="error-alert glass-panel">
            <Info color="#ff4b5c" size={20} />
            <div>
              <h4>Server Connection Alert</h4>
              <p>{error}</p>
            </div>
          </div>
        )}

        {/* TAB 1: RECOMMENDATIONS */}
        {activeTab === 'recommendations' && (
          <div className="tab-pane">
            <header className="pane-header">
              <div>
                <h1>Personalized Content Discovery</h1>
                <p>Select a user profile to explore latent factor recommendation scores & explanations.</p>
              </div>
              <div className="user-select-container">
                <Users size={16} className="input-icon" />
                <select 
                  value={selectedUserId || ''} 
                  onChange={(e) => setSelectedUserId(Number(e.target.value))}
                  className="user-select"
                >
                  {users.map(u => (
                    <option key={u.user_id} value={u.user_id}>
                      User {u.user_id} ({u.ratings_count} ratings)
                    </option>
                  ))}
                </select>
              </div>
            </header>

            {/* Selected User Stats Summary */}
            {selectedUserId && userHistory.length > 0 && (
              <div className="stats-grid">
                <div className="stat-card glass-panel">
                  <UserCheck size={20} className="stat-icon cyan" />
                  <div>
                    <h3>{userHistory.length}</h3>
                    <p>Total Ratings</p>
                  </div>
                </div>
                <div className="stat-card glass-panel">
                  <TrendingUp size={20} className="stat-icon red" />
                  <div>
                    <h3>
                      {(userHistory.reduce((acc, curr) => acc + curr.rating, 0) / userHistory.length).toFixed(2)}
                    </h3>
                    <p>Average Rating Given</p>
                  </div>
                </div>
                <div className="stat-card glass-panel">
                  <History size={20} className="stat-icon gold" />
                  <div>
                    <h3>{userHistory.filter(h => h.rating >= 4).length}</h3>
                    <p>High Ratings (&ge; 4★)</p>
                  </div>
                </div>
              </div>
            )}

            {/* Recommendations Grid */}
            <section className="recommendations-section">
              <h2>Top Recommendations for You</h2>
              {recLoading ? (
                <div className="skeleton-grid">
                  {[...Array(4)].map((_, i) => (
                    <div key={i} className="skeleton-card glass-panel animate-pulse"></div>
                  ))}
                </div>
              ) : (
                <div className="recommendations-grid">
                  {recommendations.map(movie => (
                    <div key={movie.movie_id} className="movie-card glass-panel">
                      <div className="movie-header">
                        <div className="movie-badge">SVD Rank</div>
                        <span className="movie-score">{movie.predicted_rating.toFixed(1)} ★</span>
                      </div>
                      <div className="movie-details">
                        <h3 className="movie-title">{movie.title}</h3>
                        <span className="movie-year">{movie.year}</span>
                      </div>
                      <div className="explanation-box">
                        <Info size={14} className="explanation-icon" />
                        <p className="explanation-text">{movie.explanation}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>

            {/* User Historical Ratings */}
            <section className="history-section">
              <h2>User Historical Ratings</h2>
              <div className="table-container glass-panel">
                <table className="history-table">
                  <thead>
                    <tr>
                      <th>Movie Title</th>
                      <th>Release Year</th>
                      <th>Rating Given</th>
                      <th>Date Rated</th>
                    </tr>
                  </thead>
                  <tbody>
                    {userHistory.slice(0, 8).map(hist => (
                      <tr key={hist.movie_id}>
                        <td className="hist-title">{hist.title}</td>
                        <td>{hist.year}</td>
                        <td>
                          <span className={`star-badge ${hist.rating >= 4 ? 'high' : hist.rating <= 2 ? 'low' : ''}`}>
                            {hist.rating} ★
                          </span>
                        </td>
                        <td className="hist-date">{hist.date}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </div>
        )}

        {/* TAB 2: SIMILARITY EXPLORER */}
        {activeTab === 'explorer' && (
          <div className="tab-pane">
            <header className="pane-header">
              <div>
                <h1>Item-to-Item Similarity Explorer</h1>
                <p>Search for a movie inside the Netflix database and discover similar titles calculated from user rating correlations.</p>
              </div>
            </header>

            <div className="explorer-grid">
              {/* Left Column: Search panel */}
              <div className="search-panel glass-panel">
                <div className="search-box">
                  <Search size={18} className="search-box-icon" />
                  <input 
                    type="text" 
                    placeholder="Search movie title (e.g. Dinosaur, Isle, Character)..." 
                    value={searchQuery}
                    onChange={handleSearch}
                    className="search-input"
                  />
                </div>

                {searchLoading ? (
                  <div className="search-loading animate-pulse">Searching titles...</div>
                ) : (
                  <div className="search-results">
                    {searchResults.length === 0 && searchQuery && (
                      <p className="empty-message">No matching movies found.</p>
                    )}
                    {searchResults.map(movie => (
                      <button 
                        key={movie.movie_id}
                        onClick={() => selectMovieForSimilarity(movie)}
                        className={`search-result-item ${selectedMovie?.movie_id === movie.movie_id ? 'active' : ''}`}
                      >
                        <div>
                          <h4>{movie.title}</h4>
                          <p>{movie.year}</p>
                        </div>
                        <ChevronRight size={16} />
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Right Column: Similarity Details */}
              <div className="similarity-results-panel">
                {selectedMovie ? (
                  <div className="glass-panel results-inner">
                    <div className="selected-movie-header">
                      <Film size={28} className="selected-movie-icon" />
                      <div>
                        <h2>{selectedMovie.title}</h2>
                        <p>Netflix Movie ID: {selectedMovie.movie_id} | Year: {selectedMovie.year}</p>
                      </div>
                    </div>

                    <h3>Similar Movies (Cosine Correlation)</h3>
                    {similarLoading ? (
                      <div className="spinner-container">
                        <div className="spinner"></div>
                      </div>
                    ) : similarMovies.length === 0 ? (
                      <p className="empty-message">No similarity weights computed for this item.</p>
                    ) : (
                      <div className="similar-movies-grid">
                        {similarMovies.map(sim => (
                          <div key={sim.movie_id} className="similar-movie-card glass-panel">
                            <div className="similarity-score-bar">
                              <span className="similarity-percent">{(sim.similarity * 100).toFixed(0)}% Match</span>
                              <div className="bar-bg">
                                <div className="bar-fill" style={{ width: `${sim.similarity * 100}%` }}></div>
                              </div>
                            </div>
                            <h4>{sim.title}</h4>
                            <p>Released: {sim.year}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="glass-panel empty-results-state">
                    <Film size={48} className="empty-state-icon" />
                    <h3>No Movie Selected</h3>
                    <p>Search and select a movie from the list on the left to explore its similarity neighbors.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: DASHBOARD STATS & ANALYTICS */}
        {activeTab === 'analytics' && stats && (
          <div className="tab-pane">
            <header className="pane-header">
              <div>
                <h1>Interactive Dashboard & Analytics</h1>
                <p>Analyze density, movie metrics, and SVD vs. KNN prediction performance comparisons.</p>
              </div>
            </header>

            {/* Quick Metrics */}
            <div className="stats-grid">
              <div className="stat-card glass-panel">
                <Database size={20} className="stat-icon cyan" />
                <div>
                  <h3>{stats.total_ratings.toLocaleString()}</h3>
                  <p>Subset Ratings</p>
                </div>
              </div>
              <div className="stat-card glass-panel">
                <Users size={20} className="stat-icon red" />
                <div>
                  <h3>{stats.total_users.toLocaleString()}</h3>
                  <p>Active Users</p>
                </div>
              </div>
              <div className="stat-card glass-panel">
                <Film size={20} className="stat-icon gold" />
                <div>
                  <h3>{stats.total_movies.toLocaleString()}</h3>
                  <p>Subset Movies</p>
                </div>
              </div>
              <div className="stat-card glass-panel">
                <Layers size={20} className="stat-icon cyan" />
                <div>
                  <h3>{stats.sparsity.toFixed(1)}%</h3>
                  <p>Matrix Sparsity</p>
                </div>
              </div>
            </div>

            {/* Visualization Charts Grid */}
            <div className="charts-grid">
              {/* Rating Distribution Custom SVG Bar Chart */}
              <div className="chart-container glass-panel">
                <h3>Rating Score Distribution</h3>
                <div className="svg-chart-wrapper">
                  <svg viewBox="0 0 500 250" className="svg-chart">
                    {/* Gridlines */}
                    <line x1="50" y1="50" x2="450" y2="50" stroke="rgba(255,255,255,0.05)" />
                    <line x1="50" y1="100" x2="450" y2="100" stroke="rgba(255,255,255,0.05)" />
                    <line x1="50" y1="150" x2="450" y2="150" stroke="rgba(255,255,255,0.05)" />
                    <line x1="50" y1="200" x2="450" y2="200" stroke="rgba(255,255,255,0.15)" />

                    {/* Gradient Definition */}
                    <defs>
                      <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#e50914" />
                        <stop offset="100%" stopColor="#ff4b5c" />
                      </linearGradient>
                    </defs>

                    {/* Plot Bars */}
                    {Object.entries(stats.rating_distribution).map(([rating, val], idx) => {
                      const maxVal = Math.max(...Object.values(stats.rating_distribution));
                      const barHeight = (val / maxVal) * 130;
                      const xPos = 80 + idx * 75;
                      const yPos = 200 - barHeight;

                      return (
                        <g key={rating}>
                          <rect 
                            x={xPos} 
                            y={yPos} 
                            width="40" 
                            height={barHeight} 
                            fill="url(#barGrad)" 
                            rx="4"
                            className="chart-bar"
                          />
                          {/* Value label */}
                          <text 
                            x={xPos + 20} 
                            y={yPos - 8} 
                            fill="#ffffff" 
                            fontSize="10" 
                            textAnchor="middle"
                          >
                            {val > 1000000 ? `${(val/1000000).toFixed(1)}M` : `${(val/1000).toFixed(0)}k`}
                          </text>
                          {/* Axis Label */}
                          <text 
                            x={xPos + 20} 
                            y="220" 
                            fill="#9aa0b0" 
                            fontSize="12" 
                            textAnchor="middle"
                          >
                            {rating}★
                          </text>
                        </g>
                      );
                    })}
                  </svg>
                </div>
              </div>

              {/* Model Comparison SVG Bar Chart */}
              <div className="chart-container glass-panel">
                <h3>Prediction vs. Ranking (SVD vs. KNN)</h3>
                <div className="svg-chart-wrapper">
                  <svg viewBox="0 0 500 250" className="svg-chart">
                    {/* Gridlines */}
                    <line x1="50" y1="50" x2="450" y2="50" stroke="rgba(255,255,255,0.05)" />
                    <line x1="50" y1="125" x2="450" y2="125" stroke="rgba(255,255,255,0.05)" />
                    <line x1="50" y1="200" x2="450" y2="200" stroke="rgba(255,255,255,0.15)" />

                    <defs>
                      <linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#0072ff" />
                        <stop offset="100%" stopColor="#00d2ff" />
                      </linearGradient>
                      <linearGradient id="redGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#e50914" />
                        <stop offset="100%" stopColor="#ff4b5c" />
                      </linearGradient>
                    </defs>

                    {/* SVD Bars */}
                    {/* RMSE (0.8160) -> Height is proportional */}
                    <rect x="90" y={200 - 0.8160 * 150} width="35" height={0.8160 * 150} fill="url(#blueGrad)" rx="3" />
                    <text x="107" y={192 - 0.8160 * 150} fill="#ffffff" fontSize="10" textAnchor="middle">0.816</text>

                    {/* MAP@10 (0.7427) */}
                    <rect x="135" y={200 - 0.7427 * 150} width="35" height={0.7427 * 150} fill="url(#redGrad)" rx="3" />
                    <text x="152" y={192 - 0.7427 * 150} fill="#ffffff" fontSize="10" textAnchor="middle">0.743</text>

                    {/* KNN Bars */}
                    {/* RMSE (0.8553) */}
                    <rect x="290" y={200 - 0.8553 * 150} width="35" height={0.8553 * 150} fill="url(#blueGrad)" rx="3" />
                    <text x="307" y={192 - 0.8553 * 150} fill="#ffffff" fontSize="10" textAnchor="middle">0.855</text>

                    {/* MAP@10 (0.7079) */}
                    <rect x="335" y={200 - 0.7079 * 150} width="35" height={0.7079 * 150} fill="url(#redGrad)" rx="3" />
                    <text x="352" y={192 - 0.7079 * 150} fill="#ffffff" fontSize="10" textAnchor="middle">0.708</text>

                    {/* Legend & X Axis */}
                    <text x="130" y="222" fill="#ffffff" fontSize="12" textAnchor="middle" fontWeight="bold">SVD (Latent Factor)</text>
                    <text x="330" y="222" fill="#ffffff" fontSize="12" textAnchor="middle" fontWeight="bold">KNN (Item-Based)</text>

                    {/* Legend Markers */}
                    <rect x="410" y="50" width="12" height="12" fill="url(#blueGrad)" rx="2" />
                    <text x="428" y="60" fill="#9aa0b0" fontSize="10">RMSE</text>

                    <rect x="410" y="70" width="12" height="12" fill="url(#redGrad)" rx="2" />
                    <text x="428" y="80" fill="#9aa0b0" fontSize="10">MAP@10</text>
                  </svg>
                </div>
              </div>
            </div>

            {/* Top movies listing */}
            <div className="top-movies-section glass-panel">
              <h3>Top Rated Content in Netflix Subset (Min. 1,000 Ratings)</h3>
              <div className="top-movies-list">
                {stats.top_movies.map((movie, idx) => (
                  <div key={idx} className="top-movie-item">
                    <div className="movie-index">#{idx + 1}</div>
                    <div className="movie-info">
                      <h4>{movie.title}</h4>
                      <p>{movie.ratings_count.toLocaleString()} ratings</p>
                    </div>
                    <div className="movie-rating">{movie.avg_rating.toFixed(2)} ★</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
