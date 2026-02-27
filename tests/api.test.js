'use strict';
const { describe, it, before, after } = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const supertest = require('supertest');

// Re-require the app fresh for each test run (reset module cache won't work cleanly
// for the shared arrays, so we import the app module once and rely on its shared state).
const { app, businesses, reviews } = require('../server');

const request = supertest(app);

describe('GET /api/businesses', () => {
  it('returns an array of businesses with computed fields', async () => {
    const res = await request.get('/api/businesses').expect(200);
    assert.ok(Array.isArray(res.body));
    assert.ok(res.body.length >= 3);
    const first = res.body[0];
    assert.ok('averageRating' in first);
    assert.ok('reviewCount' in first);
  });
});

describe('GET /api/businesses/:id', () => {
  it('returns a single business', async () => {
    const res = await request.get('/api/businesses/1').expect(200);
    assert.equal(res.body.id, 1);
    assert.equal(res.body.name, 'The Golden Fork');
  });

  it('returns 404 for unknown id', async () => {
    await request.get('/api/businesses/9999').expect(404);
  });
});

describe('POST /api/businesses', () => {
  it('creates a new business', async () => {
    const res = await request
      .post('/api/businesses')
      .send({ name: 'Test Biz', category: 'Testing' })
      .expect(201);
    assert.equal(res.body.name, 'Test Biz');
    assert.equal(res.body.category, 'Testing');
    assert.ok(res.body.id);
  });

  it('returns 400 when name is missing', async () => {
    await request
      .post('/api/businesses')
      .send({ category: 'Testing' })
      .expect(400);
  });

  it('returns 400 when category is missing', async () => {
    await request
      .post('/api/businesses')
      .send({ name: 'Test Biz' })
      .expect(400);
  });
});

describe('GET /api/businesses/:id/reviews', () => {
  it('returns reviews for a business', async () => {
    const res = await request.get('/api/businesses/1/reviews').expect(200);
    assert.ok(Array.isArray(res.body));
    assert.ok(res.body.length >= 2);
    assert.equal(res.body[0].businessId, 1);
  });

  it('returns 404 for unknown business', async () => {
    await request.get('/api/businesses/9999/reviews').expect(404);
  });
});

describe('POST /api/businesses/:id/reviews', () => {
  it('creates a review', async () => {
    const res = await request
      .post('/api/businesses/1/reviews')
      .send({ author: 'Tester', rating: 4, comment: 'Great!' })
      .expect(201);
    assert.equal(res.body.businessId, 1);
    assert.equal(res.body.rating, 4);
    assert.equal(res.body.author, 'Tester');
  });

  it('returns 400 when rating is missing', async () => {
    await request
      .post('/api/businesses/1/reviews')
      .send({ author: 'Tester' })
      .expect(400);
  });

  it('returns 400 when rating is out of range', async () => {
    await request
      .post('/api/businesses/1/reviews')
      .send({ author: 'Tester', rating: 6 })
      .expect(400);
  });

  it('returns 400 when author is missing', async () => {
    await request
      .post('/api/businesses/1/reviews')
      .send({ rating: 3 })
      .expect(400);
  });

  it('returns 404 for unknown business', async () => {
    await request
      .post('/api/businesses/9999/reviews')
      .send({ author: 'Tester', rating: 3 })
      .expect(404);
  });
});

describe('averageRating calculation', () => {
  it('reflects new reviews in the business listing', async () => {
    // Get original average for business 3 (1 review, rating 4)
    const before = await request.get('/api/businesses/3').expect(200);
    assert.equal(before.body.averageRating, 4);

    // Add a rating of 2
    await request
      .post('/api/businesses/3/reviews')
      .send({ author: 'TestUser', rating: 2 })
      .expect(201);

    // Average should now be (4 + 2) / 2 = 3
    const after = await request.get('/api/businesses/3').expect(200);
    assert.equal(after.body.averageRating, 3);
  });
});
