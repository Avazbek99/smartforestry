from app import app, db, SuperAdmin

def check_db():
    with app.app_context():
        # Check tables
        try:
            admin = SuperAdmin.query.filter_by(username='superadmin').first()
            if admin:
                print(f"User 'superadmin' FOUND. Hash: {admin.password_hash[:10]}...")
            else:
                print("User 'superadmin' NOT FOUND.")
                
            # Create if missing
            if not admin:
                print("Creating superadmin...")
                new_admin = SuperAdmin(username='superadmin')
                new_admin.set_password('admin123')
                db.session.add(new_admin)
                db.session.commit()
                print("SuperAdmin created successfully.")
        except Exception as e:
            print(f"Error accessing DB: {e}")
            # Try creating tables if they don't exist logic failed earlier
            try:
                db.create_all()
                print("Tables created.")
                new_admin = SuperAdmin(username='superadmin')
                new_admin.set_password('admin123')
                db.session.add(new_admin)
                db.session.commit()
                print("SuperAdmin created.")
            except Exception as e2:
                print(f"Critical Error: {e2}")

if __name__ == "__main__":
    check_db()
