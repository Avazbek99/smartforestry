import os
from app import app, db, SuperAdmin, Admin, Region

def verify_login():
    client = app.test_client()
    
    with app.app_context():
        # Ensure superadmin exists
        sa = SuperAdmin.query.filter_by(username='superadmin').first()
        if not sa:
            sa = SuperAdmin(username='superadmin')
            sa.set_password('admin123')
            db.session.add(sa)
        else:
            sa.set_password('admin123')
            
        # Create a dummy region and admin for testing if not exists
        region = Region.query.filter_by(slug='test-region').first()
        if not region:
            region = Region(name='Test Region', slug='test-region')
            db.session.add(region)
            db.session.commit()
            
        admin = Admin.query.filter_by(username='testadmin').first()
        if not admin:
            admin = Admin(username='testadmin', region_id=region.id)
            admin.set_password('password123')
            db.session.add(admin)
        else:
            admin.set_password('password123')
        
        db.session.commit()
        
        # 1. Test SuperAdmin Login
        print("Testing SuperAdmin login...")
        response = client.post('/admin/login', data={
            'username': 'superadmin',
            'password': 'admin123'
        }, follow_redirects=True)
        if response.status_code != 200:
            print(f"SuperAdmin Login failed with status {response.status_code}")
            print(response.data.decode('utf-8')[:500])
        assert response.status_code == 200
        if b"SuperAdmin Panel" not in response.data and b"Jami hududlar" not in response.data:
            print("SuperAdmin Dashboard content not found")
            print(response.data.decode('utf-8')[:500])
        assert b"SuperAdmin Panel" in response.data or b"Jami hududlar" in response.data
        print("SuperAdmin Login: PASSED")
        
        # Logout
        client.get('/logout')
        
        # 2. Test Region Admin Login
        print("Testing Region Admin login...")
        response = client.post('/admin/login', data={
            'username': 'testadmin',
            'password': 'password123'
        }, follow_redirects=True)
        if response.status_code != 200:
            print(f"Region Admin Login failed with status {response.status_code}")
        assert response.status_code == 200
        if b"testadmin" not in response.data:
            print("Region Admin Dashboard content ('testadmin') not found")
            # Check for common keywords in admin dashboard
            print(f"Final URL: {response.request.url}")
            print(f"Response snippet: {response.data.decode('utf-8')[:1000]}")
        assert b"testadmin" in response.data
        print("Region Admin Login: PASSED")
        
        # 3. Test Invalid Login
        print("Testing invalid login...")
        response = client.post('/admin/login', data={
            'username': 'nonexistent',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert b"noto" in response.data or b"xato" in response.data
        print("Invalid Login: PASSED")

if __name__ == "__main__":
    verify_login()
