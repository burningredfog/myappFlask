import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'defaultsecretkey')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Ścieżka do pliku sqlite w folderze instance/
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'dev.db')
    _db_url = os.getenv('DATABASE_URL')
    if not _db_url:
        instance_dir = os.path.join(basedir, 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        _db_url = f"sqlite:///{os.path.join(instance_dir, DATABASE_NAME)}"
    SQLALCHEMY_DATABASE_URI = _db_url

    # --- KONFIGURACJA MAILA ---
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 'yes']
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')  # Twój email
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # Hasło lub hasło aplikacji
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    MAIL_RECIPIENT = os.getenv("MAIL_RECIPIENT")

    # --- KONFIGURACJA PLIKÓW ---
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    THUMBNAIL_FOLDER = os.path.join('static', 'uploads', 'thumbs')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_MIME = {'image/jpeg', 'image/png', 'image/gif'}
    MAX_SINGLE_FILE = 8 * 1024 * 1024  # 8MB na plik


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'