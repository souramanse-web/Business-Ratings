# Business Rating App

A Flask web application that allows users to rate and review businesses organized by sector. Features user authentication, admin panel, and comprehensive rating system.

## Features

- 🏢 **Browse Businesses by Sector** - Organized business directory by industry
- ⭐ **Rate & Review** - Users can rate businesses (1-5 stars) with optional comments
- 👤 **User Authentication** - Secure registration and login system
- 🔐 **Admin Panel** - Manage sectors, businesses, and view statistics
- 📊 **Analytics** - View average ratings and rating counts per business
- 🔄 **Update Ratings** - Users can update their own ratings anytime

## Project Structure

```
├── app.py                 # Flask application with database models & routes
├── requirements.txt       # Python dependencies
├── templates/
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Home page
│   ├── sector_detail.html # Sector view with businesses
│   ├── business_detail.html # Business details & rating form
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   └── admin_dashboard.html # Admin management panel
├── static/               # Static files (CSS, JS)
└── business_ratings.db   # SQLite database (created on first run)
```

## Setup

### 1. Create a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Initialize the database:
```bash
flask init-db
```

### 4. (Optional) Seed with sample data:
```bash
flask seed-db
```

## Running

```bash
python app.py
```

The server will start on `http://localhost:5000`

## Default Routes

- **`/`** – Home page with sectors
- **`/sector/<id>`** – View businesses in a sector
- **`/business/<id>`** – View business details and ratings
- **`/register`** – User registration
- **`/login`** – User login
- **`/logout`** – User logout
- **`/admin`** – Admin dashboard (admin access only)

## API Endpoints

### Business Data
- **GET `/api/businesses`** – List all businesses (optional: `?sector_id=<id>`)
- **GET `/api/ratings/business/<id>`** – Get ratings for a business

### Ratings (Requires Authentication)
- **POST `/api/rate`** – Submit a rating
  ```json
  {
    "business_id": 1,
    "score": 5,
    "comment": "Great service!"
  }
  ```

### Admin (Requires Admin Access)
- **GET `/admin/sectors`** – List all sectors
- **POST `/admin/sectors`** – Create new sector
- **GET `/admin/businesses`** – List all businesses
- **POST `/admin/businesses`** – Create new business
- **DELETE `/admin/business/<id>`** – Delete a business

## Making a User Admin

After registering a user, run:
```bash
flask make-admin <username>
```

## Database Models

### User
- id, username, email, password_hash, is_admin, created_at
- Relations: ratings (one-to-many)

### Sector
- id, name, description, created_at
- Relations: businesses (one-to-many)

### Business
- id, name, description, sector_id, website, location, created_at
- Relations: ratings (one-to-many)

### Rating
- id, score (1-5), comment, user_id, business_id, created_at
- Relations: user, business

## Requirements

Python 3.7 or higher