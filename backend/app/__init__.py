from flask import Flask
from config import Config, TestingConfig  
from app.extensions import db, migrate, jwt, cache
from flask_cors import CORS
from app.logging_config import setup_logging

def create_app(config_class=Config):
    """Application factory."""
    app = Flask(__name__)

        # Load the specified config class
    if config_class == "testing":
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(Config)
    # app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cache.init_app(app)
    
    # Configure logging
    setup_logging(app)

    # Configure CORS
    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://127.0.0.1:3000", "http://localhost:3000"]}},
        supports_credentials=True
    )

    # Register blueprints
    with app.app_context():
        from app.routes import register_blueprints
        register_blueprints(app)

    # Register error handlers
    with app.app_context():
        from app.errors.handlers import register_error_handlers
        register_error_handlers(app)

    return app
