/* global app.js – Business Ratings frontend */
'use strict';

// ─── Utilities ────────────────────────────────────────────────────────────────

function starsHTML(rating, max = 5) {
  let html = '<span class="stars" aria-label="' + (rating ? rating + ' out of 5 stars' : 'No ratings yet') + '">';
  for (let i = 1; i <= max; i++) {
    html += '<span class="star ' + (rating && i <= Math.round(rating) ? 'filled' : 'empty') + '">★</span>';
  }
  html += '</span>';
  return html;
}

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Request failed');
  return data;
}

// ─── Business List ─────────────────────────────────────────────────────────────

async function loadBusinesses() {
  const list = document.getElementById('business-list');
  try {
    const businesses = await fetchJSON('/api/businesses');
    if (businesses.length === 0) {
      list.innerHTML = '<p class="empty">No businesses yet. Add one above!</p>';
      return;
    }
    list.innerHTML = businesses.map(renderBusinessCard).join('');
    list.querySelectorAll('.view-btn').forEach((btn) => {
      btn.addEventListener('click', () => openBusinessModal(parseInt(btn.dataset.id, 10)));
    });
  } catch (err) {
    list.innerHTML = '<p class="empty">Failed to load businesses.</p>';
    console.error(err);
  }
}

function renderBusinessCard(b) {
  const rating = b.averageRating;
  return `
    <div class="business-card">
      <span class="category-badge">${escapeHtml(b.category)}</span>
      <h3>${escapeHtml(b.name)}</h3>
      ${b.address ? `<p class="address">📍 ${escapeHtml(b.address)}</p>` : ''}
      ${b.description ? `<p class="description">${escapeHtml(b.description)}</p>` : ''}
      <div class="rating-summary">
        ${starsHTML(rating)}
        <span class="rating-text">${rating ? rating + ' / 5 (' + b.reviewCount + ' review' + (b.reviewCount !== 1 ? 's' : '') + ')' : 'No reviews yet'}</span>
      </div>
      <div class="card-actions">
        <button class="btn btn-outline view-btn" data-id="${b.id}">View &amp; Rate</button>
      </div>
    </div>`;
}

// ─── Business Detail Modal ─────────────────────────────────────────────────────

async function openBusinessModal(id) {
  const overlay = document.getElementById('modal-overlay');
  const content = document.getElementById('modal-content');
  overlay.classList.remove('hidden');
  content.innerHTML = '<p class="loading">Loading…</p>';

  try {
    const [business, reviews] = await Promise.all([
      fetchJSON(`/api/businesses/${id}`),
      fetchJSON(`/api/businesses/${id}/reviews`),
    ]);
    content.innerHTML = renderDetail(business, reviews);
    initStarPicker(id);
    initReviewForm(id);
  } catch (err) {
    content.innerHTML = '<p class="empty">Failed to load business details.</p>';
    console.error(err);
  }
}

function renderDetail(b, reviews) {
  const rating = b.averageRating;
  return `
    <div class="detail-header">
      <span class="category-badge">${escapeHtml(b.category)}</span>
      <h2 id="modal-title">${escapeHtml(b.name)}</h2>
      ${b.address ? `<p class="address">📍 ${escapeHtml(b.address)}</p>` : ''}
      ${b.description ? `<p class="description">${escapeHtml(b.description)}</p>` : ''}
      <div class="detail-stats">
        ${rating ? `<span class="big-rating">${rating}</span>${starsHTML(rating)}` : ''}
        <span class="review-count">${b.reviewCount} review${b.reviewCount !== 1 ? 's' : ''}</span>
      </div>
    </div>

    <div class="reviews-section">
      <h3>Reviews</h3>
      <div class="review-list" id="review-list">
        ${reviews.length === 0
          ? '<p class="no-reviews">No reviews yet. Be the first!</p>'
          : reviews.map(renderReview).join('')}
      </div>
    </div>

    <div class="submit-review">
      <h3>Leave a Review</h3>
      <form id="review-form">
        <div class="form-group" style="margin-bottom:.75rem">
          <label for="review-author">Your Name <span class="required">*</span></label>
          <input type="text" id="review-author" placeholder="Your name" required />
        </div>
        <div class="form-group" style="margin-bottom:.75rem">
          <label>Your Rating <span class="required">*</span></label>
          <div class="star-picker" id="star-picker" role="group" aria-label="Rating">
            ${[1,2,3,4,5].map((n) => `<button type="button" class="star-btn" data-value="${n}" aria-label="${n} star${n>1?'s':''}">★</button>`).join('')}
          </div>
          <input type="hidden" id="review-rating" value="" />
        </div>
        <div class="form-group" style="margin-bottom:.85rem">
          <label for="review-comment">Comment (optional)</label>
          <input type="text" id="review-comment" placeholder="Share your experience…" />
        </div>
        <button type="submit" class="btn btn-primary">Submit Review</button>
        <p id="review-msg" class="form-msg" aria-live="polite"></p>
      </form>
    </div>`;
}

function renderReview(r) {
  return `
    <div class="review-item">
      <div class="review-meta">
        <span class="review-author">${escapeHtml(r.author)}</span>
        <span class="review-date">${r.date}</span>
      </div>
      ${starsHTML(r.rating)}
      ${r.comment ? `<p class="review-comment">${escapeHtml(r.comment)}</p>` : ''}
    </div>`;
}

// ─── Star Picker ───────────────────────────────────────────────────────────────

function initStarPicker() {
  const picker = document.getElementById('star-picker');
  const ratingInput = document.getElementById('review-rating');
  let selected = 0;

  picker.querySelectorAll('.star-btn').forEach((btn) => {
    const val = parseInt(btn.dataset.value, 10);

    btn.addEventListener('mouseenter', () => highlightStars(val));
    btn.addEventListener('mouseleave', () => highlightStars(selected));
    btn.addEventListener('click', () => {
      selected = val;
      ratingInput.value = val;
      highlightStars(val);
    });
  });

  function highlightStars(upTo) {
    picker.querySelectorAll('.star-btn').forEach((b) => {
      b.classList.toggle('selected', parseInt(b.dataset.value, 10) <= upTo);
    });
  }
}

// ─── Review Form ───────────────────────────────────────────────────────────────

function initReviewForm(businessId) {
  const form = document.getElementById('review-form');
  const msg = document.getElementById('review-msg');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    msg.textContent = '';
    msg.className = 'form-msg';

    const author = document.getElementById('review-author').value.trim();
    const rating = document.getElementById('review-rating').value;
    const comment = document.getElementById('review-comment').value.trim();

    if (!author) { showMsg(msg, 'Please enter your name.', 'error'); return; }
    if (!rating)  { showMsg(msg, 'Please select a star rating.', 'error'); return; }

    try {
      const review = await fetchJSON(`/api/businesses/${businessId}/reviews`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ author, rating: parseInt(rating, 10), comment }),
      });

      // Prepend the new review
      const list = document.getElementById('review-list');
      const noReviews = list.querySelector('.no-reviews');
      if (noReviews) noReviews.remove();
      list.insertAdjacentHTML('afterbegin', renderReview(review));

      form.reset();
      document.getElementById('review-rating').value = '';
      document.getElementById('star-picker').querySelectorAll('.star-btn').forEach((b) => b.classList.remove('selected'));

      showMsg(msg, 'Thank you for your review!', 'success');

      // Refresh list to update average rating
      loadBusinesses();
    } catch (err) {
      showMsg(msg, err.message || 'Failed to submit review.', 'error');
    }
  });
}

function showMsg(el, text, type) {
  el.textContent = text;
  el.className = 'form-msg ' + type;
}

// ─── Add Business Form ─────────────────────────────────────────────────────────

function initAddBusinessForm() {
  const form = document.getElementById('add-business-form');
  const msg = document.getElementById('add-business-msg');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    msg.textContent = '';
    msg.className = 'form-msg';

    const name = document.getElementById('biz-name').value.trim();
    const category = document.getElementById('biz-category').value.trim();
    const address = document.getElementById('biz-address').value.trim();
    const description = document.getElementById('biz-description').value.trim();

    try {
      await fetchJSON('/api/businesses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, category, address, description }),
      });
      form.reset();
      showMsg(msg, `"${escapeHtml(name)}" added successfully!`, 'success');
      loadBusinesses();
    } catch (err) {
      showMsg(msg, err.message || 'Failed to add business.', 'error');
    }
  });
}

// ─── Modal Close ───────────────────────────────────────────────────────────────

function initModal() {
  const overlay = document.getElementById('modal-overlay');
  document.getElementById('modal-close').addEventListener('click', () => {
    overlay.classList.add('hidden');
  });
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) overlay.classList.add('hidden');
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') overlay.classList.add('hidden');
  });
}

// ─── Init ──────────────────────────────────────────────────────────────────────

initModal();
initAddBusinessForm();
loadBusinesses();
