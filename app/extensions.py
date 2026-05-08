from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
<<<<<<< email-verification
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
=======
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
>>>>>>> main
