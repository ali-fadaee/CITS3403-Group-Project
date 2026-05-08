<<<<<<< email-verification
from flask import Flask, render_template, request
from sqlalchemy.orm import selectinload
from app.extensions import db, migrate, mail
=======
from flask import Flask
from app.extensions import db, migrate, login_manager
>>>>>>> main
from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
<<<<<<< email-verification
    mail.init_app(app)
=======
    login_manager.init_app(app)
>>>>>>> main

    from app import models
    from app.routes import main
    app.register_blueprint(main)

    return app
