from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
    admins = db.relationship('Admin', backref='region', lazy=True)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    
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
    admin = db.relationship('Admin', backref='news')
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    region = db.relationship('Region', backref='news')

def login_required_superadmin(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'superadmin_id' not in session:
            return redirect(url_for('superadmin_login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_admin(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_regions():
    return dict(regions=Region.query.all())

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')
    region_id = request.args.get('region_id', type=int)
    
    query = News.query
    
    if search_query:
        query = query.filter(News.title.contains(search_query) | News.content.contains(search_query))
    
    if region_id:
        query = query.filter_by(region_id=region_id)
        
    pagination = query.order_by(News.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    news_list = pagination.items
    
    return render_template('index.html', news_list=news_list, pagination=pagination, search_query=search_query, current_region_id=region_id)

@app.route('/admin/login', methods=['GET', 'POST'])
def superadmin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Avval SuperAdmin ni tekshiramiz
        superadmin = SuperAdmin.query.filter_by(username=username).first()
        if superadmin and superadmin.check_password(password):
            session['superadmin_id'] = superadmin.id
            return redirect(url_for('superadmin_dashboard'))
        
        # Agar SuperAdmin bo'lmasa, Admin ni tekshiramiz
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['region_id'] = admin.region_id
            return redirect(url_for('admin_dashboard', region_slug=admin.region.slug))
        
        flash('Login yoki parol noto\'g\'ri')
    return render_template('login.html')

@app.route('/<region_slug>/login', methods=['GET', 'POST'])
def admin_login(region_slug):
    region = Region.query.filter_by(slug=region_slug).first_or_404()
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username, region_id=region.id).first()
        
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['region_id'] = region.id
            return redirect(url_for('admin_dashboard', region_slug=region_slug))
        flash('Login yoki parol noto\'g\'ri')
    
    return render_template('admin_login.html', region=region)

@app.route('/admin/dashboard')
@login_required_superadmin
def superadmin_dashboard():
    regions = Region.query.all()
    admins = Admin.query.all()
    return render_template('superadmin_dashboard.html', regions=regions, admins=admins)

@app.route('/admin/region/add', methods=['GET', 'POST'])
@login_required_superadmin
def add_region():
    if request.method == 'POST':
        name = request.form['name']
        slug = request.form['slug']
        
        if Region.query.filter_by(slug=slug).first():
            flash('Bu hudud allaqachon mavjud')
            return redirect(url_for('add_region'))
        
        region = Region(name=name, slug=slug)
        db.session.add(region)
        db.session.commit()
        flash('Hudud muvaffaqiyatli qo\'shildi')
        return redirect(url_for('superadmin_dashboard'))
    
    return render_template('add_region.html')

@app.route('/admin/admin/add', methods=['GET', 'POST'])
@login_required_superadmin
def add_admin():
    regions = Region.query.all()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        region_id = request.form['region_id']
        
        if Admin.query.filter_by(username=username).first():
            flash('Bu admin allaqachon mavjud')
            return redirect(url_for('add_admin'))
        
        admin = Admin(username=username, region_id=region_id)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        flash('Admin muvaffaqiyatli qo\'shildi')
        return redirect(url_for('superadmin_dashboard'))
    
    return render_template('add_admin.html', regions=regions)

@app.route('/<region_slug>/dashboard')
@login_required_admin
def admin_dashboard(region_slug):
    region = Region.query.filter_by(slug=region_slug).first_or_404()
    admin = Admin.query.get(session['admin_id'])
    news_list = News.query.filter_by(region_id=region.id).order_by(News.created_at.desc()).all()
    return render_template('admin_dashboard.html', region=region, admin=admin, news_list=news_list)

@app.route('/<region_slug>/news/add', methods=['GET', 'POST'])
@login_required_admin
def add_news(region_slug):
    region = Region.query.filter_by(slug=region_slug).first_or_404()
    admin = Admin.query.get(session['admin_id'])
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        admin_id = session['admin_id']
        
        news = News(title=title, content=content, admin_id=admin_id, region_id=region.id)
        db.session.add(news)
        db.session.commit()
        flash('Yangilik muvaffaqiyatli qo\'shildi')
        return redirect(url_for('admin_dashboard', region_slug=region_slug))
    
    return render_template('add_news.html', region=region, admin=admin)

@app.route('/<region_slug>/news/<int:news_id>/edit', methods=['GET', 'POST'])
@login_required_admin
def edit_news(region_slug, news_id):
    region = Region.query.filter_by(slug=region_slug).first_or_404()
    news = News.query.get_or_404(news_id)
    admin = Admin.query.get(session['admin_id'])
    
    if news.admin_id != admin.id and 'superadmin_id' not in session:
        flash('Siz faqat o\'zingizning yangiliklaringizni tahrirlay olmaysiz')
        return redirect(url_for('admin_dashboard', region_slug=region_slug))
    
    if request.method == 'POST':
        news.title = request.form['title']
        news.content = request.form['content']
        db.session.commit()
        flash('Yangilik muvaffaqiyatli tahrirlandi')
        return redirect(url_for('admin_dashboard', region_slug=region_slug))
    
    return render_template('edit_news.html', region=region, news=news, admin=admin)

@app.route('/<region_slug>/news/<int:news_id>/delete', methods=['POST'])
@login_required_admin
def delete_news(region_slug, news_id):
    news = News.query.get_or_404(news_id)
    admin = Admin.query.get(session['admin_id'])
    
    if news.admin_id != admin.id and 'superadmin_id' not in session:
        flash('Siz faqat o\'zingizning yangiliklaringizni o\'chira olmaysiz')
        return redirect(url_for('admin_dashboard', region_slug=region_slug))
    
    db.session.delete(news)
    db.session.commit()
    flash('Yangilik muvaffaqiyatli o\'chirildi')
    return redirect(url_for('admin_dashboard', region_slug=region_slug))

@app.route('/admin/news/<int:news_id>/delete', methods=['POST'])
@login_required_superadmin
def superadmin_delete_news(news_id):
    news = News.query.get_or_404(news_id)
    region_slug = news.region.slug
    db.session.delete(news)
    db.session.commit()
    flash('Yangilik muvaffaqiyatli o\'chirildi')
    return redirect(url_for('superadmin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        if not SuperAdmin.query.filter_by(username='superadmin').first():
            superadmin = SuperAdmin(username='superadmin')
            superadmin.set_password('admin123')
            db.session.add(superadmin)
            db.session.commit()
            print("SuperAdmin created: username='superadmin', password='admin123'")
    
    app.run(debug=True)
