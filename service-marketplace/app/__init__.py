import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()


def create_app(config_class=None):
    from .config import DevelopmentConfig

    app = Flask(__name__, static_folder="static", template_folder="templates")

    if config_class is None:
        config_class = DevelopmentConfig

    app.config.from_object(config_class)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "main.login"
    login_manager.login_message_category = "info"

    from .routes import main_bp

    app.register_blueprint(main_bp)

    return app
