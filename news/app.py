from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# --------------------
# APP CONFIG
# --------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# SQLite (Render uchun to‘g‘ri joy)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/news.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --------------------
# MODELS
# --------------------
class SuperAdmin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)

    region = db.relationship('Region', backref='admins')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)

    admin = db.relationship('Admin', backref='news')
    region = db.relationship('Region', backref='news')


# --------------------
# DATABASE INIT (ENG MUHIM QISM)
# --------------------
with app.app_context():
    db.create_all()

    # SuperAdmin avtomatik yaratiladi (agar yo‘q bo‘lsa)
    if not SuperAdmin.query.filter_by(username='superadmin').first():
        sa = SuperAdmin(username='superadmin')
        sa.set_password('admin123')
        db.session.add(sa)
        db.session.commit()
        print("SuperAdmin created: superadmin / admin123")


# --------------------
# AUTH DECORATORS
# --------------------
from functools import wraps

def login_required_superadmin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'superadmin_id' not in session:
            return redirect(url_for('superadmin_login'))
        return f(*args, **kwargs)
    return wrapper


def login_required_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return wrapper


# --------------------
# CONTEXT
# --------------------
@app.context_processor
def inject_regions():
    return dict(regions=Region.query.all())


# --------------------
# ROUTES
# --------------------
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    query = News.query.order_by(News.created_at.desc())
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    return render_template(
        'index.html',
        news_list=pagination.items,
        pagination=pagination
    )


@app.route('/admin/login', methods=['GET', 'POST'])
def superadmin_login():
    if request.method == 'POST':
        user = SuperAdmin.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            session['superadmin_id'] = user.id
            return redirect(url_for('superadmin_dashboard'))
        flash('Login yoki parol noto‘g‘ri')
    return render_template('login.html')


@app.route('/admin/dashboard')
@login_required_superadmin
def superadmin_dashboard():
    return render_template(
        'superadmin_dashboard.html',
        regions=Region.query.all(),
        admins=Admin.query.all()
    )


@app.route('/admin/region/add', methods=['GET', 'POST'])
@login_required_superadmin
def add_region():
    if request.method == 'POST':
        region = Region(
            name=request.form['name'],
            slug=request.form['slug']
        )
        db.session.add(region)
        db.session.commit()
        return redirect(url_for('superadmin_dashboard'))
    return render_template('add_region.html')


@app.route('/admin/admin/add', methods=['GET', 'POST'])
@login_required_superadmin
def add_admin():
    regions = Region.query.all()
    if request.method == 'POST':
        admin = Admin(
            username=request.form['username'],
            region_id=request.form['region_id']
        )
        admin.set_password(request.form['password'])
        db.session.add(admin)
        db.session.commit()
        return redirect(url_for('superadmin_dashboard'))
    return render_template('add_admin.html', regions=regions)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
