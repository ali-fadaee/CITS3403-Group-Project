from flask import Flask
from app.extensions import db, migrate, login_manager
from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app import models
    from app.routes import main
    app.register_blueprint(main)

    return app
