from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize app
app = Flask(__name__)
app.config.from_object('app.config.Config')

# Initialize database and migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirects if user is not logged in

# Import routes and models
from app import routes, models

# User Loader Function (for Flask-Login)
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
