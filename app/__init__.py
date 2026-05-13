from flask import Flask

from app.config import Config
from app.extensions import db, csrf, limiter, login_manager, mail, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if not app.config.get('SECRET_KEY'):
        raise RuntimeError('SECRET_KEY environment variable is not set.')

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    from app import models
    from app.routes import main

    app.register_blueprint(main)

    return app
