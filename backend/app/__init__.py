import os
from flask import Flask, send_from_directory, request, g, current_app, session
from dotenv import load_dotenv
from celery import Celery, Task
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_babel import Babel
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .oauth import init_oauth

load_dotenv()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
babel = Babel()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)
_redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
celery = Celery(__name__, broker=_redis_url)

def get_locale():
    # Check if user has selected a language in session
    if 'language' in session and session['language'] in current_app.config['LANGUAGES']:
        return session['language']
    
    # Fall back to browser language preference
    return request.accept_languages.best_match(current_app.config['LANGUAGES']) or 'en'

def create_app(test_config=None):
    app = Flask(__name__)
    if not os.getenv('SECRET_KEY') and not test_config:
        raise ValueError("Nie znaleziono SECRET_KEY. Upewnij się, że plik .env istnieje i zawiera tę zmienną.")

    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY'),
        UPLOAD_FOLDER=os.path.join(app.root_path, 'uploads'),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        GOOGLE_CLIENT_ID=os.getenv('GOOGLE_CLIENT_ID'),
        GOOGLE_CLIENT_SECRET=os.getenv('GOOGLE_CLIENT_SECRET'),
        GOOGLE_ANALYTICS_ID=os.getenv('GOOGLE_ANALYTICS_ID'),  # SEO: Google Analytics tracking ID
        SENTRY_DSN=os.getenv('SENTRY_DSN'),  # Security: Sentry error tracking
        STRIPE_PUBLISHABLE_KEY=os.getenv('STRIPE_PUBLISHABLE_KEY'),
        STRIPE_SECRET_KEY=os.getenv('STRIPE_SECRET_KEY'),
        STRIPE_WEBHOOK_SECRET=os.getenv('STRIPE_WEBHOOK_SECRET'),
        ADMIN_EMAIL=os.getenv('ADMIN_EMAIL'),
        ADMIN_PASSWORD=os.getenv('ADMIN_PASSWORD'),
        BABEL_DEFAULT_LOCALE='en',
        LANGUAGES=['en', 'pl'],
        BABEL_TRANSLATION_DIRECTORIES=os.path.join(app.root_path, 'translations'),
        CELERY_BROKER_URL=_redis_url,
        CELERY_RESULT_BACKEND=_redis_url,
        # Session configuration for proper cookie handling
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true',  # True in production with HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        PERMANENT_SESSION_LIFETIME=2592000,  # 30 days
    )
    if test_config: app.config.update(test_config)

    # Initialize Sentry for error tracking (production only)
    if app.config['SENTRY_DSN'] and not app.config['TESTING']:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration
        
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[
                FlaskIntegration(),
                CeleryIntegration(),
            ],
            traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
            profiles_sample_rate=0.1,  # 10% for profiling
        )

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Initialize limiter only if not testing
    if not app.config.get('TESTING'):
        limiter.init_app(app)
    
    init_oauth(app)
    babel.init_app(app, locale_selector=get_locale)
    login_manager.login_view = 'auth.login'

    @app.before_request
    def before_request():
        g.locale = get_locale()

    celery.conf.update(app.config)
    class ContextTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context(): return self.run(*args, **kwargs)
    celery.Task = ContextTask

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.route('/uploads/<path:filename>')
    def serve_uploads(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    from . import models, commands
    commands.register_commands(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(models.User, int(user_id))

    from .blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    from .blueprints.audio import bp as audio_bp
    app.register_blueprint(audio_bp)
    from .blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)
    from .blueprints.billing import bp as billing_bp
    app.register_blueprint(billing_bp)
    from .blueprints.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    return app
