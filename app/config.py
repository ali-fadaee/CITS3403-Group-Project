import os

basedir = os.path.abspath(os.path.dirname(__file__))
default_db_path = "sqlite:///" + os.path.join(basedir, "app.db")


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or default_db_path
    SECRET_KEY = os.getenv("SECRET_KEY")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "sandbox.smtp.mailtrap.io")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 2525))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
