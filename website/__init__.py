# website/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv

# ---------------------------------------
# Load .env
# ---------------------------------------
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(base_dir, ".env"))

# ---------------------------------------
# Extensions (global)
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
    # DATABASE CONFIG
    # ---------------------------------------
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

    # Fallback for local SQLite when no DB is provided
    if POSTGRES_USER and POSTGRES_PASSWORD and POSTGRES_DB:
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
            f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )
    else:
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
    # BLUEPRINTS
    # ---------------------------------------
    from .views import views
    from .auth import auth

    app.register_blueprint(views)
    app.register_blueprint(auth)

    # ---------------------------------------
    # DATABASE TABLE CREATION (safe for Render)
    # ---------------------------------------
    from .models import User

    with app.app_context():
        db.create_all()

    # ---------------------------------------
    # LOGIN MANAGER
    # ---------------------------------------
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
