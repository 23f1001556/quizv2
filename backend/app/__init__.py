import os
from flask import Flask
from flask_cors import CORS
from app.configs.extensions import db, mail
from app.configs.config import DevelopmentConfig, ProductionConfig
from app.models import User, Scores, Quiz, Chapter, Subject, Question
from app.models.Ai.history import AIHistory
from app.models.study_material import StudyMaterial
from app.models.mock_quiz import MockQuiz, MockQuestion, MockAttempt
from werkzeug.security import check_password_hash

from app.auth.routes import auth_bp
from app.route.users.routes import users_bp
from app.route.subjects.routes import subjects_bp
from app.route.chapters.routes import chapters_bp
from app.route.quiz.routes import quiz_bp


def _seed_initial_user(app):
    email = app.config.get("INITIAL_USER_EMAIL")
    password = app.config.get("INITIAL_USER_PASSWORD")
    username = app.config.get("INITIAL_USER_USERNAME")

    if not email and not password:
        return
    if not email or not password:
        raise ValueError("INITIAL_USER_EMAIL and INITIAL_USER_PASSWORD must both be configured")

    email = User.format_email(email)
    username = User.format_username(username or email.split("@", 1)[0])
    if not 5 <= len(username) <= 20:
        raise ValueError("INITIAL_USER_USERNAME must be 5-20 characters")

    user = User.query.filter_by(email=email).first()
    if user:
        if user.isadmin:
            raise ValueError("Configured initial regular user email belongs to an admin account")
        if not check_password_hash(user._password, password):
            app.logger.warning("Configured initial user already exists; leaving its password unchanged")
        return

    username_owner = User.query.filter_by(user_name=username).first()
    if username_owner:
        raise ValueError("Configured initial username is already in use")

    user = User(user_name=username, email=email, isadmin=False, role="user")
    user.password = password
    user.is_verified = True
    user.is_blocked = False
    db.session.add(user)
    db.session.commit()


def create_app(test_config=None):
    app = Flask(__name__)
    # CORS(app) moved down after config loading

    env = os.getenv("DEV_ENV","testing")

    if test_config:
        app.config.update(test_config)
    elif env == "production":
        app.config.from_object("app.configs.config.ProductionConfig")
    elif env == "development":
        app.config.from_object("app.configs.config.DevelopmentConfig")
    elif env == "testing":
        app.config.from_object("app.configs.config.BaseConfig")
    else:
        raise ValueError(f"Unknown environment: {env}")

    db.init_app(app)
    mail.init_app(app)
    
    # Init CORS with config
    CORS(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS")}}, supports_credentials=True)
    
    from app.celery.config import celery_init_app
    celery_init_app(app)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(chapters_bp)
    app.register_blueprint(quiz_bp)
    
    from app.route.test_paper.routes import test_paper_bp
    app.register_blueprint(test_paper_bp)

    from app.route.ai.routes import ai_bp
    app.register_blueprint(ai_bp)

    from app.route.mock.routes import mock_bp
    app.register_blueprint(mock_bp)

    from app.route.admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all() 
        if not test_config:
            _seed_initial_user(app)

    return app