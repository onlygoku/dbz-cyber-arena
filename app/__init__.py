import os
import logging
import importlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_object=None):
    app = Flask(__name__)

    if config_object:
        if isinstance(config_object, str):
            module_name, class_name = config_object.rsplit('.', 1)
            module = importlib.import_module(module_name)
            config_object = getattr(module, class_name)
        app.config.from_object(config_object)
    else:
        from config import Config
        app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page.'
    login_manager.login_message_category = 'warning'

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.team import team_bp
    from app.routes.challenges import challenges_bp
    from app.routes.scoreboard import scoreboard_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    from app.routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(challenges_bp)
    app.register_blueprint(scoreboard_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(profile_bp)

    # Global template context
    @app.context_processor
    def inject_globals():
        from app.models.event import EventState
        state = EventState.get()
        return {
            'g_state': state,
            'app_name': app.config.get('CTF_NAME', 'Dragon Ball Z Cyber Arena'),
        }

    # Custom Jinja2 filters
    import json as _json

    @app.template_filter('fromjson')
    def fromjson_filter(value):
        try:
            return _json.loads(value) if value else []
        except Exception:
            return []

    @app.template_filter('from_json')
    def from_json_filter(value):
        try:
            return _json.loads(value) if value else []
        except Exception:
            return []

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    with app.app_context():
        try:
            db.create_all()
        except Exception:
            pass
        _bootstrap(app)

    return app


def _bootstrap(app):
    """Auto-create admin and seed event state on first run."""
    from app.models.user import User
    from app.models.event import EventState

    # Create admin
    admin_email = app.config.get('ADMIN_EMAIL', 'admin@ctf.local')
    admin_pass  = app.config.get('ADMIN_PASSWORD', 'ChangeMe123!')
    try:
        if not User.query.filter_by(email=admin_email).first():
            admin = User(
                username='admin',
                email=admin_email,
                is_admin=True,
                is_verified=True,
            )
            admin.set_password(admin_pass)
            db.session.add(admin)
            db.session.commit()
            app.logger.info(f'Admin account created: {admin_email}')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Bootstrap admin error: {e}')

    # Seed event state
    try:
        if not EventState.query.first():
            state = EventState()
            db.session.add(state)
            db.session.commit()
            app.logger.info('Event state initialised.')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Bootstrap event state error: {e}')