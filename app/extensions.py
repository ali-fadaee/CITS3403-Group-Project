from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
limiter = Limiter(key_func=get_remote_address, default_limits=[])

login_manager = LoginManager()
login_manager.login_view = "main.login"
