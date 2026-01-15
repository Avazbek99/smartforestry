from app import app, db, SuperAdmin
from werkzeug.security import generate_password_hash

def fix_superadmin():
    with app.app_context():
        db.create_all()
        
        user = SuperAdmin.query.filter_by(username='superadmin').first()
        if user:
            print("SuperAdmin user exists. Resetting password...")
            user.set_password('admin123')
        else:
            print("SuperAdmin user does NOT exist. Creating...")
            user = SuperAdmin(username='superadmin')
            user.set_password('admin123')
            db.session.add(user)
            
        db.session.commit()
        print("SuperAdmin fixed. Username: 'superadmin', Password: 'admin123'")

if __name__ == "__main__":
    fix_superadmin()
