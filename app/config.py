import os

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
default_db_path = "sqlite:///" + os.path.join(basedir, "instance", "app.db")


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or default_db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "sandbox.smtp.mailtrap.io")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 2525))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

class DeploymentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or default_db_path

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    SECRET_KEY = "test-secret-key"
    SECURITY_PASSWORD_SALT = "test-password-salt"
