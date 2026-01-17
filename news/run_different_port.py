import app

if __name__ == '__main__':
    with app.app.app_context():
        app.app.db.create_all()
        app.create_default_data()
    
    print("🚀 Starting EcoNews on port 8000...")
    print("🌐 Open: http://127.0.0.1:8000")
    app.app.run(host='127.0.0.1', port=8000, debug=True)
