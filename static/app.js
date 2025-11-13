// Main application JS (made resilient to pages that don't include every element)
// Many pages (like the login page) don't include the recommendation grids or modal
// so we guard DOM access and only initialize features present on the page.

// DOM elements (may not exist on every page like the login screen)
const mainContent = document.getElementById('mainContent');
const forYouGrid = document.getElementById('forYouGrid');
const trendingGrid = document.getElementById('trendingGrid');
const infoModalElem = document.getElementById('infoModal');
const modal = infoModalElem ? new bootstrap.Modal(infoModalElem) : null;
const modalTitle = document.getElementById('modalTitle');
const modalBody = document.getElementById('modalBody');
const themeToggle = document.getElementById('themeToggle');
const themeIcon = themeToggle ? themeToggle.querySelector('.theme-icon') : null;

// Store initial homepage content
let homepageContent = '';
if (mainContent) {
  homepageContent = mainContent.innerHTML;
}

// Helper function to get CSRF token
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// Show rating confirmation
function showRatingConfirmation(movieId, rating) {
  const message = `Rated ${rating} stars! Recommendations will update periodically.`;
  // Ensure modal elements exist before trying to access them
  const currentModal = infoModalElem ? new bootstrap.Modal(infoModalElem) : null;
  if (currentModal && modalTitle && modalBody) {
    modalTitle.textContent = 'Rating Saved';
    modalBody.textContent = message;
    currentModal.show();
  } else {
    // Fallback for pages without the modal (e.g. login)
    console.log('Rating saved:', message);
  }
}

function card(movie, local = false, userRating = 0, showWhyButton = true) {
  const col = document.createElement('div');
  col.className = 'col-12 col-sm-6 col-md-4 col-lg-3';
  
  const poster = movie.poster || 'https://via.placeholder.com/342x513?text=No+Poster';
  
  // Only show "Why?" button if it's a personalized recommendation
  const expBtn = showWhyButton ? (
    local ?
    `<button class="btn btn-sm btn-outline-primary btn-expl-local" data-id="${movie.id}">Why?</button>` :
    `<button class="btn btn-sm btn-outline-primary btn-expl-tmdb" data-tmdb="${movie.tmdb_id}" data-title="${movie.title}" data-vote="${movie.vote || 0}" data-pop="${movie.popularity || 0}">Why?</button>`
  ) : '';
  
  col.innerHTML = `
    <div class="card card-movie h-100">
      <img src="${poster}" class="poster" alt="${movie.title}"/>
      <div class="p-3 d-flex flex-column">
        <div class="fw-semibold mb-1 text-truncate" title="${movie.title}">${movie.title}</div>
        <div class="small text-muted mb-2">⭐ ${movie.vote ?? '-'} · ${movie.year ?? ''}</div>
        <div class="mt-auto d-flex flex-column gap-2">
          <div class="star-rating" data-movie-id="${movie.id || ''}" data-tmdb-id="${movie.tmdb_id || ''}" data-current-rating="${userRating}">
            ${generateInteractiveStarRating(userRating)}
            ${userRating > 0 ? `<span class="rating-value ms-2" id="user-rating-value-${movie.id || movie.tmdb_id}">${userRating}/5</span>` : ''}
          </div>
          <div class="d-flex gap-2 flex-wrap">
            ${expBtn}
            <button class="btn btn-sm btn-outline-secondary btn-trailer" data-title="${movie.title}">Trailer</button>
          </div>
        </div>
      </div>
    </div>
  `;

  // Wire up the interactive star rating if present
  const starRatingElement = col.querySelector('.star-rating');
  if (starRatingElement) wireStarRating(starRatingElement, movie.id || movie.tmdb_id, userRating);

  return col;
}

function generateStarDisplay(rating) {
  let stars = '';
  for (let i = 1; i <= 5; i++) {
    stars += `<span class="star ${i <= rating ? 'filled' : ''}">★</span>`;
  }
  return stars;
}

function generateInteractiveStarRating(currentRating) {
  let stars = '';
  for (let i = 1; i <= 5; i++) {
    stars += `<span class="star ${i <= currentRating ? 'filled' : ''}" data-rating="${i}">★</span>`;
  }
  return stars;
}

function wireStarRating(container, movieId, currentRating) {
  const stars = container.querySelectorAll('.star');
  
  // Set initial filled state
  highlightStars(container, currentRating);

  stars.forEach((star) => {
    const rating = parseInt(star.dataset.rating);
    
    star.addEventListener('mouseenter', () => highlightStars(container, rating));
    star.addEventListener('mouseleave', () => highlightStars(container, container.dataset.currentRating));
    star.addEventListener('click', () => {
      rateMovie(movieId, rating);
      container.dataset.currentRating = rating; // Update current rating
    });
  });
}

function highlightStars(container, rating) {
  const stars = container.querySelectorAll('.star');
  stars.forEach((star, index) => {
    if (index < rating) {
      star.classList.add('active');
    } else {
      star.classList.remove('active');
    }
  });
}

function clearStars(container) {
  const stars = container.querySelectorAll('.star');
  const currentRating = parseInt(container.dataset.currentRating);
  stars.forEach((star, index) => {
    if (index < currentRating) {
      star.classList.add('filled');
      star.classList.remove('active');
    } else {
      star.classList.remove('filled', 'active');
    }
  });
}

// xaiChips function removed - no longer needed with LLM explanations

async function loadForYou() {
  if (!forYouGrid) return;
  forYouGrid.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary"></div><div class="mt-2">Loading your recommendations...</div></div>';
  
  try {
    const res = await fetch('/api/recommendations/?k=12');
    const data = await res.json();
    
    // Check if user has insufficient ratings for meaningful personalization
    if (data.error === 'insufficient_ratings' || data.error === 'no_ratings') {
      const currentCount = data.current_ratings || 0;
      const requiredCount = data.required_ratings || 5;
      const remainingCount = requiredCount - currentCount;
      
      forYouGrid.innerHTML = `
        <div class="col-12">
          <div class="no-ratings-message">
            <span class="no-ratings-icon">⭐</span>
            <h5 class="no-ratings-title">${data.message}</h5>
            <p class="no-ratings-description">
              <strong>${currentCount}/${requiredCount} movies rated</strong><br>
              Rate ${remainingCount} more movie${remainingCount !== 1 ? 's' : ''} in the "Trending" section to unlock personalized recommendations!
            </p>
            <div class="progress mb-3" style="height: 8px;">
              <div class="progress-bar" role="progressbar"
                   style="width: ${(currentCount / requiredCount) * 100}%; background-color: #0d6efd;"
                   aria-valuenow="${currentCount}" aria-valuemin="0" aria-valuemax="${requiredCount}">
              </div>
            </div>
            <p class="no-ratings-hint">Content-based recommendations need at least ${requiredCount} movies to understand your preferences.</p>
          </div>
        </div>
      `;
      return;
    }
    
    const movieIds = data.map(m => m.id);
    const userRatings = await fetchUserRatings(movieIds, 'movie_id');

    forYouGrid.innerHTML = '';
    data.forEach(m => forYouGrid.appendChild(card(m, true, userRatings[m.id] || 0)));
    wireButtons(forYouGrid);
  } catch (error) {
    forYouGrid.innerHTML = '<div class="col-12"><div class="text-center text-danger py-5">Failed to load recommendations.</div></div>';
  }
}

async function loadTrending() {
  if (!trendingGrid) return;
  trendingGrid.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary"></div><div class="mt-2">Loading trending movies...</div></div>';
  
  try {
    const res = await fetch('/api/trending/?k=12');
    const data = await res.json();

    const tmdbIds = data.map(m => m.tmdb_id);
    const userRatings = await fetchUserRatings(tmdbIds, 'tmdb_id');

    trendingGrid.innerHTML = '';
    // Trending movies are general popularity-based, so no "Why?" buttons
    data.forEach(m => trendingGrid.appendChild(card(m, true, userRatings[m.tmdb_id] || 0, false))); // Correctly hide "Why?" button
    wireButtons(trendingGrid);
  } catch (error) {
    trendingGrid.innerHTML = '<div class="col-12"><div class="text-center text-danger py-5">Failed to load trending movies.</div></div>';
  }
}

// Legacy functions for compatibility
async function personalized() {
  loadForYou();
}

async function trending() {
  loadTrending();
}

async function rateMovie(movieId, rating) {
  try {
    const response = await fetch('/api/ratings/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({
        movie: movieId,
        value: rating
      })
    });
    
    if (response.ok) {
      showRatingConfirmation(movieId, rating);
      
      // Find the card's interactive star container
      const interactiveStarContainer = document.querySelector(`.star-rating[data-movie-id="${movieId}"], .star-rating[data-tmdb-id="${movieId}"]`);
      if (interactiveStarContainer) {
        // Update the interactive stars
        interactiveStarContainer.dataset.currentRating = rating;
        interactiveStarContainer.innerHTML = generateInteractiveStarRating(rating);
        wireStarRating(interactiveStarContainer, movieId, rating);

        // Update the numerical rating text
        let ratingValueSpan = interactiveStarContainer.querySelector(`#user-rating-value-${movieId}`);
        if (!ratingValueSpan) {
          // If the span doesn't exist, create it
          ratingValueSpan = document.createElement('span');
          ratingValueSpan.className = 'rating-value ms-2';
          ratingValueSpan.id = `user-rating-value-${movieId}`;
          interactiveStarContainer.appendChild(ratingValueSpan);
        }
        ratingValueSpan.textContent = `${rating}/5`;
      }

      // Removed setTimeout to immediately reload recommendations
      // Recommendations will be updated periodically or on next login
    } else {
      console.error('Failed to rate movie');
    }
  } catch (error) {
    console.error('Error rating movie:', error);
  }
}

async function discover() {
  const actor = document.getElementById('actor').value;
  const genre = document.getElementById('genre').value;
  const lang = document.getElementById('lang').value;
  
  // Construct search results HTML
  const searchResultsHtml = `
    <div id="searchResultsSection" class="mb-4">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h3 id="searchTitle">Search Results <small class="text-muted">(${actor || 'All'} ${genre || ''} ${lang || ''})</small></h3>
        <button id="btnBackToHome" class="btn btn-outline-secondary">Back to Home</button>
      </div>
      <div id="searchGrid" class="row g-3">
        <div class="col-12">
          <div class="text-center py-5">Searching TMDB…</div>
        </div>
      </div>
    </div>
  `;

  // Replace main content with search results
  if (mainContent) {
    mainContent.innerHTML = searchResultsHtml;
  } else {
    console.error("Main content container not found.");
    return;
  }

  // Get new elements from the DOM after innerHTML change
  const searchGrid = document.getElementById('searchGrid');
  const btnBackToHome = document.getElementById('btnBackToHome');

  // Wire up the back button
  if (btnBackToHome) {
    btnBackToHome.onclick = () => {
      if (mainContent) {
        mainContent.innerHTML = homepageContent; // Restore original homepage content
        // Re-initialize event listeners and load data for homepage sections
        if (forYouGrid) loadForYou();
        if (trendingGrid) loadTrending();
        wireButtons(mainContent); // Re-wire buttons for homepage
      }
    };
  }
  
  const url = new URL('/api/discover/', location.origin);
  
  if (actor) url.searchParams.set('actor', actor);
  if (genre) url.searchParams.set('genre', genre);
  if (lang) url.searchParams.set('lang', lang);
  
  try {
    const res = await fetch(url);
    const j = await res.json();
    const items = j.results || [];
    searchGrid.innerHTML = '';
    
    if (!items.length) {
      searchGrid.innerHTML = '<div class="col-12"><div class="text-center text-muted py-5">No matches. Try Genre like <b>Action</b> and language name <b>hindi</b> or ISO <b>hi</b>.</div></div>';
      return;
    }
    
    const tmdbIds = items.map(m => m.tmdb_id);
    const userRatings = await fetchUserRatings(tmdbIds, 'tmdb_id');

    items.forEach(m => {
      const col = card(m, false, userRatings[m.tmdb_id] || 0, false); // Correctly hide "Why?" button for search results
      searchGrid.appendChild(col);
    });
    wireButtons(searchGrid); // Wire buttons for search results
  } catch (e) {
    searchGrid.innerHTML = '<div class="col-12"><div class="text-center text-danger py-5">Error contacting server.</div></div>';
  }
}

async function explainLocal(id) {
  const currentModal = infoModalElem ? new bootstrap.Modal(infoModalElem) : null;
  if (!currentModal || !modalTitle || !modalBody) return;
  modalTitle.textContent = 'Why this movie?';
  modalBody.innerHTML = 'Loading personalized explanation...';
  currentModal.show();
  
  const res = await fetch(`/api/natural-explanation/?movie_id=${id}`);
  const j = await res.json();
  
  if (j.error) {
    modalBody.textContent = j.error;
    return;
  }
  
  modalBody.innerHTML =
    `<div class="mb-3">
      <h6 class="mb-2">${j.movie}</h6>
      <div class="alert alert-info">
        <p class="mb-0 mt-2">${j.explanation}</p>
      </div>
    </div>`;
}

async function explainTmdb(tmdb_id, title) {
  const currentModal = infoModalElem ? new bootstrap.Modal(infoModalElem) : null;
  if (!currentModal || !modalTitle || !modalBody) return;
  modalTitle.textContent = 'Why this movie?';
  modalBody.innerHTML = 'Loading personalized explanation...';
  currentModal.show();
  
  const res = await fetch(`/api/natural-explanation/?tmdb_id=${tmdb_id}`);
  const j = await res.json();
  
  if (j.error) {
    modalBody.textContent = j.error;
    return;
  }
  
  modalBody.innerHTML =
    `<div class="mb-3">
      <h6 class="mb-2">${j.movie || title}</h6>
      <div class="alert alert-info">
        <p class="mb-0 mt-2">${j.explanation}</p>
      </div>
    </div>`;
}

async function trailer(title) {
  const currentModal = infoModalElem ? new bootstrap.Modal(infoModalElem) : null;
  if (!currentModal || !modalTitle || !modalBody) return;
  
  // Use a robust search query for YouTube
  const searchQuery = encodeURIComponent(`${title} official trailer`);
  const youtubeSearchUrl = `https://www.youtube.com/results?search_query=${searchQuery}`;
  
  modalTitle.textContent = 'Movie Trailer';
  modalBody.innerHTML = `
    <div class="text-center py-3">
      <p>Click the button below to search for the official trailer on YouTube.</p>
      <button class="btn btn-danger" onclick="window.open('${youtubeSearchUrl}', '_blank');">
        <i class="bi bi-youtube me-2"></i> Watch Trailer on YouTube
      </button>
      <p class="mt-3 text-muted"><small>This will open a new tab with YouTube search results for "${title} official trailer".</small></p>
    </div>
  `;
  currentModal.show();
}

// Removed retryTrailerSearch function as it's no longer needed.

function wireButtons(container = document) {
  container.querySelectorAll('.btn-expl-local').forEach(btn =>
    btn.addEventListener('click', e => explainLocal(e.target.dataset.id))
  );
  
  container.querySelectorAll('.btn-expl-tmdb').forEach(btn =>
    btn.addEventListener('click', e => explainTmdb(e.target.dataset.tmdb, e.target.dataset.title)));
  
  container.querySelectorAll('.btn-trailer').forEach(btn =>
    btn.addEventListener('click', e => trailer(e.target.dataset.title)));
}

// Theme toggle functionality
function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  updateThemeIcon(newTheme);
}

// Update theme icon and title based on current theme
function updateThemeIcon(theme) {
  if (!themeToggle || !themeIcon) return;
  // Remove existing classes
  themeIcon.classList.remove('bi-sun-fill', 'bi-moon-fill');
  if (theme === 'dark') {
    themeIcon.classList.add('bi-sun-fill');
    themeToggle.setAttribute('title', 'Switch to light mode');
  } else {
    themeIcon.classList.add('bi-moon-fill');
    themeToggle.setAttribute('title', 'Switch to dark mode');
  }
}

// Initialize theme with system preference detection
function initTheme() {
  let theme = localStorage.getItem('theme');
  
  // If no saved preference, check system preference
  if (!theme) {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      theme = 'dark';
    } else {
      theme = 'light';
    }
  }
  
  document.documentElement.setAttribute('data-theme', theme);
  updateThemeIcon(theme);
  
  // Listen for system theme changes
  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
      // Only update if user hasn't manually set a preference
      if (!localStorage.getItem('theme')) {
        const newTheme = e.matches ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        updateThemeIcon(newTheme);
      }
    });
  }
}

// Event listeners
const btnDiscover = document.getElementById('btnDiscover');
if (btnDiscover) {
  btnDiscover.addEventListener('click', e => {
    e.preventDefault();
    discover();
  });
}

const btnRag = document.getElementById('btnRag');
if (btnRag) {
  btnRag.addEventListener('click', async e => {
    e.preventDefault();
    const q = prompt('Ask about a movie type:');
    if (!q) return;
    try {
      const res = await fetch('/api/rag/qa/?q=' + encodeURIComponent(q));
      const j = await res.json();
      if (modal && modalTitle && modalBody) {
        modalTitle.textContent = 'RAG Answer';
        modalBody.innerHTML = `<div class="mb-2">${j.answer || 'No answer.'}</div>` + (j.hits?.length ? `<div class="mt-2 small text-muted">Context: ${j.hits.map(h => h.title).join(', ')}</div>` : '');
        modal.show();
      }
    } catch (err) {
      console.error('RAG request failed', err);
    }
  });
}

if (themeToggle) themeToggle.addEventListener('click', toggleTheme);

// Initialize features safely
initTheme();
async function fetchUserRatings(ids, idType) {
  if (!ids || ids.length === 0) return {};
  const queryParams = new URLSearchParams();
  ids.forEach(id => queryParams.append(idType, id));

  try {
    const res = await fetch(`/api/user-ratings/?${queryParams.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch user ratings');
    const data = await res.json();
    return data; // Returns an object like {movieId: rating, ...}
  } catch (error) {
    console.error("Error fetching user ratings:", error);
    return {};
  }
}

// Initialize features safely
initTheme();
// Initial load of homepage content
if (mainContent) {
  // We need to re-fetch these elements after homepageContent is restored
  // So, no direct calls here, they will be called when homepageContent is restored
}
// For initial load, if forYouGrid and trendingGrid exist, load them
if (forYouGrid && trendingGrid) {
  loadForYou();
  loadTrending();
}
