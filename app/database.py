from app import db, app

with app.app_context():
    db.create_all()   # creates all tables
    print("Tables created successfully!")   # confirmation message