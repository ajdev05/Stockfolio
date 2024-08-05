from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash
import os

def initialize_database():
    app = create_app()
    with app.app_context():
        if not os.path.exists('stockfolio.db'):
            db.create_all()
            print("Database and tables created successfully.")
            
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                hashed_password = generate_password_hash('admin', method='pbkdf2:sha256')
                admin_user = User(username='admin', password=hashed_password)
                db.session.add(admin_user)
                db.session.commit()
                print("Admin user created successfully.")
            else:
                print("Admin user already exists.")
        else:
            print("Database already exists.")
