'use strict';

const express = require('express');
const path = require('path');

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// --- In-memory data store ---

let nextBusinessId = 4;
let nextReviewId = 6;

const businesses = [
  {
    id: 1,
    name: 'The Golden Fork',
    category: 'Restaurant',
    description: 'Upscale dining with a seasonal menu sourced from local farms.',
    address: '12 Maple Street, Springfield',
  },
  {
    id: 2,
    name: 'TechFix Pro',
    category: 'Electronics Repair',
    description: 'Fast and affordable repairs for phones, laptops, and more.',
    address: '88 Circuit Ave, Springfield',
  },
  {
    id: 3,
    name: 'Green Thumb Garden Centre',
    category: 'Garden & Nursery',
    description: 'Everything you need to grow a beautiful garden.',
    address: '5 Blossom Lane, Springfield',
  },
];

const reviews = [
  { id: 1, businessId: 1, author: 'Alice', rating: 5, comment: 'Absolutely fantastic food and service!', date: '2025-11-10' },
  { id: 2, businessId: 1, author: 'Bob', rating: 4, comment: 'Great atmosphere, slightly pricey.', date: '2025-12-03' },
  { id: 3, businessId: 2, author: 'Carol', rating: 5, comment: 'Fixed my phone in under an hour. Brilliant!', date: '2026-01-15' },
  { id: 4, businessId: 2, author: 'Dave', rating: 3, comment: 'Decent service but took longer than quoted.', date: '2026-01-28' },
  { id: 5, businessId: 3, author: 'Eve', rating: 4, comment: 'Lovely selection of plants. Staff are very helpful.', date: '2026-02-01' },
];

// --- Helper ---

function averageRating(businessId) {
  const r = reviews.filter((rv) => rv.businessId === businessId);
  if (r.length === 0) return null;
  return Math.round((r.reduce((sum, rv) => sum + rv.rating, 0) / r.length) * 10) / 10;
}

// --- API Routes ---

// List all businesses
app.get('/api/businesses', (req, res) => {
  const result = businesses.map((b) => ({
    ...b,
    averageRating: averageRating(b.id),
    reviewCount: reviews.filter((r) => r.businessId === b.id).length,
  }));
  res.json(result);
});

// Get a single business
app.get('/api/businesses/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const business = businesses.find((b) => b.id === id);
  if (!business) return res.status(404).json({ error: 'Business not found' });
  res.json({
    ...business,
    averageRating: averageRating(id),
    reviewCount: reviews.filter((r) => r.businessId === id).length,
  });
});

// Add a new business
app.post('/api/businesses', (req, res) => {
  const { name, category, description, address } = req.body;
  if (!name || !category) {
    return res.status(400).json({ error: 'name and category are required' });
  }
  const business = { id: nextBusinessId++, name, category, description: description || '', address: address || '' };
  businesses.push(business);
  res.status(201).json({ ...business, averageRating: null, reviewCount: 0 });
});

// List reviews for a business
app.get('/api/businesses/:id/reviews', (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (!businesses.find((b) => b.id === id)) {
    return res.status(404).json({ error: 'Business not found' });
  }
  const result = reviews
    .filter((r) => r.businessId === id)
    .sort((a, b) => new Date(b.date) - new Date(a.date));
  res.json(result);
});

// Submit a review for a business
app.post('/api/businesses/:id/reviews', (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (!businesses.find((b) => b.id === id)) {
    return res.status(404).json({ error: 'Business not found' });
  }
  const { author, rating, comment } = req.body;
  const ratingNum = parseInt(rating, 10);
  if (!author || !ratingNum || ratingNum < 1 || ratingNum > 5) {
    return res.status(400).json({ error: 'author and a rating between 1-5 are required' });
  }
  const review = {
    id: nextReviewId++,
    businessId: id,
    author,
    rating: ratingNum,
    comment: comment || '',
    date: new Date().toISOString().slice(0, 10),
  };
  reviews.push(review);
  res.status(201).json(review);
});

// --- Start server (only when run directly) ---

/* istanbul ignore next */
if (require.main === module) {
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => {
    console.log(`Business Ratings server running at http://localhost:${PORT}`);
  });
}

module.exports = { app, businesses, reviews };
