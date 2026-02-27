# Business Rating App - Project Instructions

This is a Flask web application for rating businesses by sector. The app includes:
- User authentication (registration/login)
- Business and sector management
- Rating and review system
- Admin dashboard for managing content

## Setup Instructions

1. **Create virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize database**
   ```bash
   flask init-db
   ```

4. **Seed sample data (optional)**
   ```bash
   flask seed-db
   ```

5. **Run the app**
   ```bash
   python app.py
   ```

The app will be available at `http://localhost:5000`

## Creating an Admin User

After registering via the web interface:
```bash
flask make-admin <username>
```

## Key Files

- `app.py` - Flask application with all routes and models
- `templates/` - HTML templates for the web interface
- `requirements.txt` - Python dependencies
- `README.md` - Complete project documentation

## Database

The app uses SQLite database (`business_ratings.db`) with the following models:
- **User** - User accounts and authentication
- **Sector** - Business sectors/industries
- **Business** - Individual business listings
- **Rating** - User ratings and reviews

## Project Status

- [x] Verify that the copilot-instructions.md file in the .github directory is created.
- [x] Clarify Project Requirements
- [x] Scaffold the Project
- [x] Customize the Project
- [x] Install Required Extensions
- [x] Compile the Project
- [x] Create and Run Task
- [ ] Launch the Project
- [x] Ensure Documentation is Complete