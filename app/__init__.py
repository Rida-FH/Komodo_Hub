from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
import os

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from app.routes import routes
    app.register_blueprint(routes)

    # ✅ Add this context processor
    @app.context_processor
    def inject_community_memberships():
        from flask import session
        from app.models import CommunityMembership, Community

        if 'user_id' in session and session.get('role') == 'community':
            user_id = session['user_id']
            memberships = CommunityMembership.query.filter_by(user_id=user_id).all()
            communities = [Community.query.get(m.community_id) for m in memberships]
            return dict(communities=communities)
        return dict(communities=[])

    return app


