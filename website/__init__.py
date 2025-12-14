# website/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv

# ---------------------------------------
# Load .env (local development only)
# ---------------------------------------
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(base_dir, ".env"))

# ---------------------------------------
# Extensions
# ---------------------------------------
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # ---------------------------------------
    # SECRET KEY
    # ---------------------------------------
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret")

    # ---------------------------------------
    # DATABASE CONFIG (Neon / Render)
    # ---------------------------------------
    db_url = os.getenv("DATABASE_URL")  # Render or Neon

    if db_url:
        # Render/Neon sometimes give "postgres://" which SQLAlchemy rejects
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)

        # Neon/Postgres requires SSL
        if "sslmode" not in db_url:
            db_url += "?sslmode=require"

        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    else:
        # Local fallback if no external DB connected
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///local.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ---------------------------------------
    # INIT EXTENSIONS
    # ---------------------------------------
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # ---------------------------------------
    # REGISTER BLUEPRINTS
    # ---------------------------------------
    from .views import views
    from .auth import auth

    app.register_blueprint(views)
    app.register_blueprint(auth)

    # ---------------------------------------
    # DATABASE TABLE CREATION (safe for Render)
    # ---------------------------------------
    with app.app_context():
        from .models import User
        db.create_all()

    # ---------------------------------------
    # LOGIN MANAGER
    # ---------------------------------------
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
