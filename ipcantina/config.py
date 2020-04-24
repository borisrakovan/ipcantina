import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'just_some_string' # fixme
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 3
    # MENU_MAX_SIZE = TODO
    # FLASK_ADMIN_SWATCH = 'cerulean'

    ALLOWED_EXTENSIONS = ['xls', 'xlsx']
    ATTACHMENTS_DIR_PATH = "attachments"
    MENU_UPLOAD_FOLDER = "uploads"
    MENU_JSON_PATH = "menu.json"
    ORDER_DEADLINE_HOUR = 15
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or "smtp.centrum.sk"
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or "ipadmin@centrum.sk"
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or "ipdevelopment"
    MAIL_ASCII_ATTACHMENTS = True
    # ADMINS = ['b.rakovan@gmail.com']
    ADMINS = ['b.rakovan@gmail.com'] # TODO
    EMAIL_BOT = 'ipadmin@centrum.sk'
