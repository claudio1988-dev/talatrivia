from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt, ma

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)

    # Register blueprints (we will create these later)
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
