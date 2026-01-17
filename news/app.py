from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import random

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')

os.makedirs(INSTANCE_DIR, exist_ok=True)

# --------------------
# APP CONFIG
# --------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# -------------------- 
# SIMPLE MULTI-LANGUAGE SUPPORT
# -------------------- 
def _(text):
    """Simple translation function"""
    lang = session.get('language', 'uz')
    
    translations = {
        'uz': {
            'Yangiliklar sayti': 'EcoNews - Ekologik Yangiliklar',
            'EcoNews': 'EcoNews',
            'So\'nggi ekologik yangiliklar': 'So\'nggi ekologik yangiliklar',
            'O\'rmonlar va yashil hududlar haqida eng so\'nggi ma\'lumotlar': 'O\'rmonlar va yashil hududlar haqida eng so\'nggi ma\'lumotlar',
            'Yangiliklarni ko\'rish': 'Yangiliklarni ko\'rish',
            'Statistika': 'Statistika',
            'Hozircha yangiliklar yo\'q': 'Hozircha yangiliklar yo\'q',
            'Tabiat uyg\'onmoqda... Tez orada yangiliklar bo\'ladi.': 'Tabiat uyg\'onmoqda... Tez orada yangiliklar bo\'ladi.',
            'To\'liq o\'qish': 'To\'liq o\'qish',
            'Yoqdi': 'Yoqdi',
            'Ulashish': 'Ulashish',
            'SuperAdmin Panel': 'SuperAdmin Panel',
            'Jami hududlar': 'Jami hududlar',
            'Jami adminlar': 'Jami adminlar',
            'Jami yangiliklar': 'Jami yangiliklar',
            'Kategoriyalar': 'Kategoriyalar',
            'Hudud qo\'shish': 'Hudud qo\'shish',
            'Admin qo\'shish': 'Admin qo\'shish',
            'Hududlar': 'Hududlar',
            'Adminlar soni': 'Adminlar soni',
            'Yangiliklar soni': 'Yangiliklar soni',
            'Barcha Yangiliklar': 'Barcha Yangiliklar',
            'Username': 'Username',
            'Hudud': 'Hudud',
            'Sarlavha': 'Sarlavha',
            'Muallif': 'Muallif',
            'Sana': 'Sana',
            'Amallar': 'Amallar',
            'Rostdan ham o\'chirmoqchimisiz?': 'Rostdan ham o\'chirmoqchimisiz?'
        },
        'uz_cyrl': {
            'Yangiliklar sayti': 'EcoNews - Экологик Янгиликлар',
            'EcoNews': 'EcoNews',
            'So\'nggi ekologik yangiliklar': 'Сўнги экологик янгиликлар',
            'O\'rmonlar va yashil hududlar haqida eng so\'nggi ma\'lumotlar': 'Ўрмонлар ва яшил ҳудудлар ҳақида энг сўнги маълумотлар',
            'Yangiliklarni ko\'rish': 'Янгиликларни кўриш',
            'Statistika': 'Статистика',
            'Hozircha yangiliklar yo\'q': 'Ҳозирча янгиликлар йўқ',
            'Tabiat uyg\'onmoqda... Tez orada yangiliklar bo\'ladi.': 'Табиат уйғонмоқда... Тез орада янгиликлар бўлади.',
            'To\'liq o\'qish': 'Тўлиқ ўқиш',
            'Yoqdi': 'Ўқди',
            'Ulashish': 'Улашиш',
            'SuperAdmin Panel': 'SuperAdmin Панел',
            'Jami hududlar': 'Жами ҳудудлар',
            'Jami adminlar': 'Жами администраторлар',
            'Jami yangiliklar': 'Жами янгиликлар',
            'Kategoriyalar': 'Категориялар',
            'Hudud qo\'shish': 'Ҳудуд қўшиш',
            'Admin qo\'shish': 'Администратор қўшиш',
            'Hududlar': 'Ҳудудлар',
            'Adminlar soni': 'Администраторлар сони',
            'Yangiliklar soni': 'Янгиликлар сони',
            'Barcha Yangiliklar': 'Барча Янгиликлар',
            'Username': 'Фойдаланувчи номи',
            'Hudud': 'Ҳудуд',
            'Sarlavha': 'Сарлавҳа',
            'Muallif': 'Муаллиф',
            'Sana': 'Сана',
            'Amallar': 'Амаллар',
            'Rostdan ham o\'chirmoqchimisiz?': 'Ростдан ҳам ўчирмоқчимисиз?'
        }
    }
    
    return translations.get(lang, {}).get(text, text)

def get_locale():
    # URL dan tilni olish
    if request.args.get('lang'):
        session['language'] = request.args.get('lang')
    return session.get('language', 'uz')

# SQLite (Render uchun to‘g‘ri joy)
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


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Font Awesome icon class


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))  # Rasm URL saqlash uchun
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    admin = db.relationship('Admin', backref='news')
    region = db.relationship('Region', backref='news')
    category = db.relationship('Category', backref='news')


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
    
    # Default kategoriyalarni yaratish
    default_categories = [
        {'name': 'O\'rmonlarni ko\'paytirish', 'slug': 'forestation', 'icon': 'fas fa-tree'},
        {'name': 'Yashil hududlar', 'slug': 'green-areas', 'icon': 'fas fa-leaf'},
        {'name': 'Cho\'llanishga qarshi kurash', 'slug': 'desertification', 'icon': 'fas fa-sun'},
        {'name': 'Ekologik ta\'lim', 'slug': 'eco-education', 'icon': 'fas fa-graduation-cap'},
        {'name': 'Xalqaro hamkorlik', 'slug': 'international', 'icon': 'fas fa-globe'},
        {'name': 'Yoshlar siyosati', 'slug': 'youth-policy', 'icon': 'fas fa-users'},
    ]
    
    for cat_data in default_categories:
        if not Category.query.filter_by(slug=cat_data['slug']).first():
            category = Category(
                name=cat_data['name'],
                slug=cat_data['slug'],
                icon=cat_data['icon']
            )
            db.session.add(category)
    
    db.session.commit()
    print("Default categories created")


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
def inject_globals():
    return dict(regions=Region.query.all(), categories=Category.query.all(), random=random)


# --------------------
# ROUTES
# -------------------- 
@app.route('/')
def index():
    get_locale()  # Set language for this request
    
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
                         news_list=news_list, 
                         pagination=pagination,
                         search_query=search_query,
                         current_region_id=region_id,
                         current_category_id=category_id,
                         _=_)


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


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin = Admin.query.filter_by(username=request.form['username']).first()
        if admin and admin.check_password(request.form['password']):
            session['admin_id'] = admin.id
            return redirect(url_for('admin_dashboard'))
        flash('Login yoki parol noto‘g‘ri')
    return render_template('admin_login.html')


@app.route('/admin/dashboard')
@login_required_admin
def admin_dashboard():
    admin = Admin.query.get(session['admin_id'])
    news_list = News.query.filter_by(admin_id=admin.id).order_by(News.created_at.desc()).all()
    return render_template('admin_dashboard.html', admin=admin, news=news_list)


@app.route('/admin/news/add', methods=['GET', 'POST'])
@login_required_admin
def add_news():
    admin = Admin.query.get(session['admin_id'])
    if request.method == 'POST':
        news = News(
            title=request.form['title'],
            content=request.form['content'],
            image_url=request.form.get('image_url'),
            admin_id=admin.id,
            region_id=admin.region_id,
            category_id=request.form.get('category_id')
        )
        db.session.add(news)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_news.html', categories=Category.query.all())


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
