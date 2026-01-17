from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_babel import Babel, gettext as _
import os

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')

os.makedirs(INSTANCE_DIR, exist_ok=True)

# -------------------- 
# APP CONFIG
# -------------------- 
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Babel configuration for multi-language support
babel = Babel(app)
app.config['LANGUAGES'] = {
    'uz': 'O\'zbekcha',
    'uz_cyrl': 'Ўзбекча (Cyrillic)'
}
app.config['BABEL_DEFAULT_LOCALE'] = 'uz'

# SQLite (Render uchun to'g'ri joy)
db_path = os.path.join(INSTANCE_DIR, 'news.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
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
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    admins = db.relationship('Admin', backref='region', lazy=True, cascade='all, delete-orphan')
    news = db.relationship('News', backref='region', lazy=True, cascade='all, delete-orphan')

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    news = db.relationship('News', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    news = db.relationship('News', backref='category', lazy=True, cascade='all, delete-orphan')

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    image_url = db.Column(db.String(500))  # Image URL field

# -------------------- 
# DECORATORS
# -------------------- 
def superadmin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'superadmin_id' not in session:
            return redirect(url_for('superadmin_login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# -------------------- 
# CONTEXT PROCESSORS
# -------------------- 
@app.context_processor
def inject_regions():
    return dict(regions=Region.query.all(), categories=Category.query.all())

# -------------------- 
# BABEL LOCALE SELECTOR (Fixed)
# -------------------- 
def get_locale():
    # URL dan tilni olish
    if request.args.get('lang'):
        session['language'] = request.args.get('lang')
    return session.get('language', 'uz')

# Set the locale selector function
babel.localeselector(get_locale)

# -------------------- 
# ROUTES
# -------------------- 
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')
    region_id = request.args.get('region_id', type=int)
    category_id = request.args.get('category_id', type=int)
    
    # Build query
    query = News.query
    
    if search_query:
        query = query.filter(News.title.contains(search_query) | News.content.contains(search_query))
    
    if region_id:
        query = query.filter(News.region_id == region_id)
    
    if category_id:
        query = query.filter(News.category_id == category_id)
    
    query = query.order_by(News.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    news_list = pagination.items
    
    return render_template('index.html', 
                         news=news_list, 
                         pagination=pagination,
                         search_query=search_query,
                         current_region_id=region_id,
                         current_category_id=category_id)

@app.route('/superadmin/login', methods=['GET', 'POST'])
def superadmin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        superadmin = SuperAdmin.query.filter_by(username=username).first()
        
        if superadmin and superadmin.check_password(password):
            session['superadmin_id'] = superadmin.id
            flash('SuperAdmin tizimga kirdi!', 'success')
            return redirect(url_for('superadmin_dashboard'))
        
        flash('Login yoki parol xato!', 'error')
    
    return render_template('superadmin_login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            flash('Admin tizimga kirdi!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        flash('Login yoki parol xato!', 'error')
    
    return render_template('admin_login.html')

@app.route('/superadmin/dashboard')
@superadmin_required
def superadmin_dashboard():
    regions = Region.query.all()
    admins = Admin.query.all()
    news = News.query.all()
    categories = Category.query.all()
    
    return render_template('superadmin_dashboard.html', 
                         regions=regions, 
                         admins=admins, 
                         news=news,
                         categories=categories)

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    admin = Admin.query.get(session['admin_id'])
    news = News.query.filter_by(admin_id=admin.id).order_by(News.created_at.desc()).all()
    
    return render_template('admin_dashboard.html', admin=admin, news=news)

@app.route('/superadmin/add_region', methods=['GET', 'POST'])
@superadmin_required
def add_region():
    if request.method == 'POST':
        name = request.form['name']
        slug = request.form['slug']
        
        region = Region(name=name, slug=slug)
        db.session.add(region)
        db.session.commit()
        
        flash('Hudud muvaffaqiyatli qo\'shildi!', 'success')
        return redirect(url_for('superadmin_dashboard'))
    
    return render_template('add_region.html')

@app.route('/superadmin/add_admin', methods=['GET', 'POST'])
@superadmin_required
def add_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        region_id = request.form['region_id']
        
        admin = Admin(username=username, region_id=region_id)
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        flash('Admin muvaffaqiyatli qo\'shildi!', 'success')
        return redirect(url_for('superadmin_dashboard'))
    
    regions = Region.query.all()
    return render_template('add_admin.html', regions=regions)

@app.route('/admin/add_news', methods=['GET', 'POST'])
@admin_required
def add_news():
    admin = Admin.query.get(session['admin_id'])
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category_id = request.form['category_id']
        image_url = request.form.get('image_url', '')
        
        news = News(title=title, content=content, admin_id=admin.id, 
                   region_id=admin.region_id, category_id=category_id, image_url=image_url)
        db.session.add(news)
        db.session.commit()
        
        flash('Yangilik muvaffaqiyatli qo\'shildi!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    categories = Category.query.all()
    return render_template('add_news.html', admin=admin, categories=categories)

@app.route('/superadmin/delete_news/<int:news_id>')
@superadmin_required
def delete_news(news_id):
    news = News.query.get_or_404(news_id)
    db.session.delete(news)
    db.session.commit()
    
    flash('Yangilik muvaffaqiyatli o\'chirildi!', 'success')
    return redirect(url_for('superadmin_dashboard'))

@app.route('/admin/delete_news/<int:news_id>')
@admin_required
def admin_delete_news(news_id):
    news = News.query.get_or_404(news_id)
    
    # Check if this admin owns this news
    if news.admin_id != session['admin_id']:
        flash('Siz faqat o\'zingiz yangiliklarini o\'chira olasiz!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    db.session.delete(news)
    db.session.commit()
    
    flash('Yangilik muvaffaqiyatli o\'chirildi!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/superadmin/delete_region/<int:region_id>')
@superadmin_required
def delete_region(region_id):
    region = Region.query.get_or_404(region_id)
    db.session.delete(region)
    db.session.commit()
    
    flash('Hudud muvaffaqiyatli o\'chirildi!', 'success')
    return redirect(url_for('superadmin_dashboard'))

@app.route('/superadmin/delete_admin/<int:admin_id>')
@superadmin_required
def delete_admin(admin_id):
    admin = Admin.query.get_or_404(admin_id)
    db.session.delete(admin)
    db.session.commit()
    
    flash('Admin muvaffaqiyatli o\'chirildi!', 'success')
    return redirect(url_for('superadmin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Tizimdan chiqdingiz!', 'info')
    return redirect(url_for('index'))

# -------------------- 
# INITIALIZATION
# -------------------- 
def create_default_data():
    """Create default SuperAdmin and categories if they don't exist"""
    
    # Create default SuperAdmin
    if SuperAdmin.query.filter_by(username='superadmin').first() is None:
        superadmin = SuperAdmin(username='superadmin')
        superadmin.set_password('admin123')
        db.session.add(superadmin)
        db.session.commit()
        print("Default SuperAdmin created: superadmin/admin123")
    
    # Create default categories
    default_categories = [
        {'name': 'forestation', 'slug': 'forestation'},
        {'name': 'green-areas', 'slug': 'green-areas'},
        {'name': 'desertification', 'slug': 'desertification'},
        {'name': 'eco-education', 'slug': 'eco-education'},
        {'name': 'international', 'slug': 'international'},
        {'name': 'youth-policy', 'slug': 'youth-policy'}
    ]
    
    for cat_data in default_categories:
        if Category.query.filter_by(slug=cat_data['slug']).first() is None:
            category = Category(name=cat_data['name'], slug=cat_data['slug'])
            db.session.add(category)
    
    db.session.commit()
    print("Default categories created")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_data()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
