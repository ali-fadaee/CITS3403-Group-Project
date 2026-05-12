from flask import Flask
from flask_wtf.csrf import generate_csrf

from app.config import Config
from app.extensions import db, limiter, login_manager, mail, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    @app.context_processor
    def csrf_context():
        return dict(csrf_token=generate_csrf)

    from app import models
    from app.routes import main

    app.register_blueprint(main)

    return app
