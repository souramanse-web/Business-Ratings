"""
Business Rating Application
A Flask app to rate businesses by sector with user authentication and admin panel.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
import click
import os
from translations import get_translation

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
database_url = os.environ.get('DATABASE_URL', 'sqlite:///business_ratings.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SAMESITE'] = 'Lax'

is_production = os.environ.get('RENDER') == 'true' or bool(os.environ.get('DATABASE_URL'))
if is_production:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['REMEMBER_COOKIE_SECURE'] = True
else:
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['REMEMBER_COOKIE_SECURE'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
db_ready_checked = False

# =====================
# Context Processors & Utilities
# =====================

@app.context_processor
def inject_user():
    """Inject current user and language into templates"""
    lang = session.get('lang', 'en')
    return {
        'current_user': current_user,
        'current_lang': lang,
        't': lambda key: get_translation(key, lang)
    }

@app.before_request
def set_language():
    """Set language from session or default to English"""
    global db_ready_checked

    if is_production and not db_ready_checked:
        try:
            inspector = inspect(db.engine)
            if not inspector.has_table('user'):
                ensure_database_ready()
            db_ready_checked = True
        except SQLAlchemyError:
            db.session.rollback()

    if 'lang' not in session:
        session['lang'] = 'en'

@app.route('/set-language/<lang>')
def set_language_route(lang):
    """Change language preference"""
    if lang in ['en', 'fr']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))
# =====================

class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ratings = db.relationship('Rating', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Sector(db.Model):
    """Business sector/industry model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    businesses = db.relationship('Business', backref='sector', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class Business(db.Model):
    """Business model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    sector_id = db.Column(db.Integer, db.ForeignKey('sector.id'), nullable=False)
    website = db.Column(db.String(255))
    location = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ratings = db.relationship('Rating', backref='business', lazy=True, cascade='all, delete-orphan')

    def get_average_rating(self):
        if not self.ratings:
            return 0
        return round(sum(r.score for r in self.ratings) / len(self.ratings), 2)

    def get_rating_count(self):
        return len(self.ratings)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'sector': self.sector.name if self.sector else None,
            'website': self.website,
            'location': self.location,
            'average_rating': self.get_average_rating(),
            'rating_count': self.get_rating_count()
        }


class Rating(db.Model):
    """Business rating model"""
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'score': self.score,
            'comment': self.comment,
            'username': self.user.username,
            'business_name': self.business.name,
            'created_at': self.created_at.isoformat()
        }


def ensure_database_ready():
    """Create database tables and optionally bootstrap an admin user from env vars."""
    db.create_all()

    admin_username = os.environ.get('ADMIN_BOOTSTRAP_USERNAME')
    admin_email = os.environ.get('ADMIN_BOOTSTRAP_EMAIL')
    admin_password = os.environ.get('ADMIN_BOOTSTRAP_PASSWORD')

    if admin_username and admin_email and admin_password:
        existing_user = User.query.filter_by(username=admin_username).first()
        if not existing_user:
            admin_user = User(username=admin_username, email=admin_email, is_admin=True)
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
        else:
            existing_user.email = admin_email
            existing_user.is_admin = True
            existing_user.set_password(admin_password)
            db.session.commit()


def seed_sample_data(reset_businesses: bool = True):
    """Seed sectors and businesses. Optionally clear ratings/businesses first."""
    sectors_data = [
        {'name': 'Banks', 'description': 'Banks and Banking Services - Personal and Business Banking'},
        {'name': 'Insurance', 'description': 'Insurance Companies - Auto, Health, Home, and Life Insurance'},
        {'name': 'Hotels', 'description': 'Hotels and Hospitality - Accommodations and Travel Services'},
        {'name': 'Technology', 'description': 'Software, hardware, IT services'},
        {'name': 'Retail', 'description': 'Clothing, electronics, general merchandise'},
        {'name': 'Clinics', 'description': 'Hospitals, clinics, medical services'},
        {'name': 'Food & Beverage', 'description': 'Restaurants, cafes, food delivery'},
    ]

    for sector_data in sectors_data:
        existing_sector = Sector.query.filter_by(name=sector_data['name']).first()
        if not existing_sector:
            db.session.add(Sector(name=sector_data['name'], description=sector_data['description']))
        else:
            existing_sector.description = sector_data['description']

    db.session.commit()

    sectors_by_name = {sector.name: sector for sector in Sector.query.all()}

    if reset_businesses:
        Rating.query.delete()
        Business.query.delete()
        db.session.commit()

    businesses_data = [
        {'name': 'Coris Bank', 'description': 'Full-service banking solutions', 'sector': 'Banks', 'location': 'New York', 'website': 'https://example.com'},
        {'name': 'Bank Of Africa', 'description': 'Community-focused banking', 'sector': 'Banks', 'location': 'Atlanta', 'website': ''},
        {'name': 'Ecobank', 'description': 'Pan-African banking services', 'sector': 'Banks', 'location': 'Lomé', 'website': ''},
        {'name': 'Atlantic Bank', 'description': 'Corporate and investment banking', 'sector': 'Banks', 'location': 'London', 'website': ''},

        {'name': 'SafeGuard Insurance', 'description': 'Auto and home insurance', 'sector': 'Insurance', 'location': 'Chicago', 'website': 'https://example.com'},
        {'name': 'HealthShield Inc', 'description': 'Health insurance provider', 'sector': 'Insurance', 'location': 'Boston', 'website': ''},
        {'name': 'LifeSecure Insurance', 'description': 'Life and disability insurance', 'sector': 'Insurance', 'location': 'Denver', 'website': ''},

        {'name': 'Grand Plaza Hotel', 'description': 'Luxury 5-star hotel with premium amenities', 'sector': 'Hotels', 'location': 'New York', 'website': 'https://example.com'},
        {'name': 'Comfort Inn Express', 'description': 'Budget-friendly accommodations', 'sector': 'Hotels', 'location': 'Austin', 'website': ''},
        {'name': 'Seaside Resort', 'description': 'Beachfront resort with spa facilities', 'sector': 'Hotels', 'location': 'Miami', 'website': ''},

        {'name': 'TechCorp', 'description': 'Leading software solutions', 'sector': 'Technology', 'location': 'San Francisco', 'website': ''},
        {'name': 'StyleHub', 'description': 'Fashion and accessories', 'sector': 'Retail', 'location': 'New York', 'website': ''},
        {'name': 'HealthPlus', 'description': 'Modern medical center', 'sector': 'Clinics', 'location': 'Boston', 'website': ''},
    ]

    created_businesses = 0
    for business_data in businesses_data:
        sector = sectors_by_name.get(business_data['sector'])
        if not sector:
            continue

        existing_business = Business.query.filter_by(name=business_data['name']).first()
        if not existing_business:
            business = Business(
                name=business_data['name'],
                description=business_data['description'],
                sector_id=sector.id,
                website=business_data['website'],
                location=business_data['location']
            )
            db.session.add(business)
            created_businesses += 1

    db.session.commit()

    return {
        'sectors': Sector.query.count(),
        'businesses': Business.query.count(),
        'created_businesses': created_businesses,
    }


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    ensure_database_ready()


# =====================
# Routes - Authentication
# =====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'Registration successful'}), 201

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return jsonify({'message': 'Login successful'}), 200

        return jsonify({'error': 'Invalid credentials'}), 401

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# =====================
# Routes - Main Pages
# =====================

@app.route('/')
def index():
    sectors = Sector.query.all()
    return render_template('index.html', sectors=sectors)


@app.route('/sector/<int:sector_id>')
def sector_detail(sector_id):
    sector = Sector.query.get_or_404(sector_id)
    businesses = Business.query.filter_by(sector_id=sector_id).all()
    return render_template('sector_detail.html', sector=sector, businesses=businesses)


@app.route('/business/<int:business_id>')
def business_detail(business_id):
    business = Business.query.get_or_404(business_id)
    ratings = Rating.query.filter_by(business_id=business_id).order_by(Rating.created_at.desc()).all()
    return render_template('business_detail.html', business=business, ratings=ratings)


@app.route('/healthz', methods=['GET'])
def healthz():
    return jsonify({'status': 'ok'}), 200


# =====================
# Routes - API (Ratings)
# =====================

@app.route('/api/businesses', methods=['GET'])
def get_businesses():
    sector_id = request.args.get('sector_id', type=int)
    if sector_id:
        businesses = Business.query.filter_by(sector_id=sector_id).all()
    else:
        businesses = Business.query.all()

    return jsonify([b.to_dict() for b in businesses])


@app.route('/api/rate', methods=['POST'])
@login_required
def rate_business():
    data = request.get_json(silent=True) or {}
    business_id = data.get('business_id')
    score = data.get('score')
    comment = data.get('comment', '')

    try:
        business_id = int(business_id)
        score = int(score)
    except (TypeError, ValueError):
        return jsonify({'error': 'business_id and score must be integers'}), 400

    if not 1 <= score <= 5:
        return jsonify({'error': 'Score must be between 1 and 5'}), 400

    # Check if business exists
    business = Business.query.get_or_404(business_id)

    # Remove existing rating from this user for this business if it exists
    existing_rating = Rating.query.filter_by(
        user_id=current_user.id,
        business_id=business_id
    ).first()

    if existing_rating:
        existing_rating.score = score
        existing_rating.comment = comment
    else:
        rating = Rating(
            score=score,
            comment=comment,
            user_id=current_user.id,
            business_id=business_id
        )
        db.session.add(rating)

    db.session.commit()
    return jsonify({'message': 'Rating saved', 'average_rating': business.get_average_rating()}), 201


@app.route('/api/ratings/business/<int:business_id>', methods=['GET'])
def get_business_ratings(business_id):
    ratings = Rating.query.filter_by(business_id=business_id).all()
    return jsonify([r.to_dict() for r in ratings])


# =====================
# Routes - Admin Panel
# =====================

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('index'))

    sectors_count = Sector.query.count()
    businesses_count = Business.query.count()
    ratings_count = Rating.query.count()
    users_count = User.query.count()

    return render_template('admin_dashboard.html',
                         sectors_count=sectors_count,
                         businesses_count=businesses_count,
                         ratings_count=ratings_count,
                         users_count=users_count)


@app.route('/admin/sectors', methods=['GET', 'POST', 'DELETE'])
@login_required
def admin_sectors():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'POST':
        data = request.get_json()
        sector = Sector(name=data.get('name'), description=data.get('description', ''))
        db.session.add(sector)
        db.session.commit()
        return jsonify(sector.to_dict()), 201

    sectors = Sector.query.all()
    return jsonify([s.to_dict() for s in sectors])


@app.route('/admin/businesses', methods=['GET', 'POST'])
@login_required
def admin_businesses():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'POST':
        data = request.get_json()
        business = Business(
            name=data.get('name'),
            description=data.get('description', ''),
            sector_id=data.get('sector_id'),
            website=data.get('website', ''),
            location=data.get('location', '')
        )
        db.session.add(business)
        db.session.commit()
        return jsonify(business.to_dict()), 201

    businesses = Business.query.all()
    return jsonify([b.to_dict() for b in businesses])


@app.route('/admin/business/<int:business_id>', methods=['DELETE'])
@login_required
def admin_delete_business(business_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    business = Business.query.get_or_404(business_id)
    db.session.delete(business)
    db.session.commit()
    return jsonify({'message': 'Business deleted'}), 200


@app.route('/admin/seed', methods=['POST'])
@login_required
def admin_seed_data():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    summary = seed_sample_data(reset_businesses=True)
    return jsonify({
        'message': 'Sample sectors and companies loaded successfully',
        'summary': summary
    }), 200


# =====================
# Error Handlers
# =====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


# =====================
# CLI Commands for Database Setup
# =====================

@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Initialized the database.')


@app.cli.command()
def seed_db():
    """Seed the database with sample data."""
    summary = seed_sample_data(reset_businesses=True)
    print(
        f"Database seeded with sample data. "
        f"Sectors: {summary['sectors']}, Businesses: {summary['businesses']}"
    )


@app.cli.command()
@click.argument('username')
def make_admin(username):
    """Make a user an admin. Usage: flask make-admin <username>"""
    user = User.query.filter_by(username=username).first()

    if not user:
        print(f'User {username} not found.')
        return

    user.is_admin = True
    db.session.commit()
    print(f'User {username} is now an admin.')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
