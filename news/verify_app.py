import os
import uuid
import time
from datetime import datetime, timedelta
from app import app, db, News, Region, Admin

def verify_app():
    # Use a unique test database file
    unique_id = str(uuid.uuid4())[:8]
    test_db_file = f'test_news_{unique_id}.db'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.abspath(test_db_file)}'
    app.config['TESTING'] = True
    
    print(f"Using DB: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Remove session if any exists
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        
        # Create test data
        region_slug = f"eco-region-{unique_id}"
        region = Region(name=f"Eco Region {unique_id}", slug=region_slug)
        db.session.add(region)
        db.session.commit()
        
        admin = Admin(username=f"ecoadmin_{unique_id}", region_id=region.id)
        admin.set_password("admin")
        db.session.add(admin)
        db.session.commit()
        
        # Add news with desc order logic
        # We want 'Green News 4' to be on page 2.
        # Order by created_at DESC.
        # Latest = 14, Oldest = 0.
        # Page 1 (10 items): 14..5
        # Page 2 (5 items): 4..0
        
        news_items = []
        base_time = datetime.utcnow()
        for i in range(15):
             # Ensure explicit order: i=0 is oldest, i=14 is newest
            created_at = base_time + timedelta(minutes=i)
            news = News(
                title=f"Green News {i}", 
                content=f"Content about nature and ecology {i}",
                admin_id=admin.id,
                region_id=region.id,
                created_at=created_at
            )
            news_items.append(news)
        db.session.add_all(news_items)
        db.session.commit()
        
        client = app.test_client()
        
        # 1. Test Search
        response = client.get(f'/?q=Green News 1')
        assert response.status_code == 200
        assert b"Green News 1" in response.data
        print("Search Verification: PASSED")
        
        # 2. Test Pagination
        response = client.get('/?page=2')
        assert response.status_code == 200
        # Check for News 4
        if b"Green News 4" in response.data:
            print("Pagination Verification: PASSED")
        else:
            print("Pagination Verification: FAILED (News 4 not found on page 2)")
            print(f"Page 2 content snippet: {response.data[:500]}")
        
        # 3. Test Region Filter
        response = client.get(f'/?region_id={region.id}')
        assert response.status_code == 200
        if region.name.encode() in response.data:
             print("Region Filter Verification: PASSED")
        else:
             print("Region Filter Verification: FAILED")

    # Cleanup
    try:
        if os.path.exists(test_db_file):
            os.remove(test_db_file)
            print("Cleanup: PASSED")
    except:
        pass

if __name__ == "__main__":
    verify_app()
