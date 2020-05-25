import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '43e654d66f4e46b1b4de27e2416e8c30'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                                'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER_NAME = os.environ.get('SERVER_NAME')
    # SERVER_NAME = "cantina.ipcentrum.sk"
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']

    INSTRUCTIONS_TEXT_PATH = os.environ.get('INSTRUCTIONS_TEXT_PATH')
    DEFAULT_PRICES_PATH = os.environ.get('DEFAULT_PRICES_PATH')
    ATTACHMENTS_DIR_PATH = os.environ.get('ATTACHMENTS_DIR_PATH')
    MENU_UPLOAD_FOLDER = os.environ.get('MENU_UPLOAD_FOLDER')

    MENU_JSON_PATH = os.environ.get('MENU_JSON_PATH')

    ORDER_DEADLINE_HOUR = os.environ.get('ORDER_DEADLINE_HOUR') or 15

    MEAL_BOX_PRICE = 0.3

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))

    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_ASCII_ATTACHMENTS = True
    # ADMINS = ['b.rakovan@gmail.com']
    # ADMINS = ['b.rakovan@gmail.com', 'p.skoda@ipdevelopment.sk']
    # ADMINS = ['b.rakovan@gmail.com', 'p.skoda@ipdevelopment.sk', 'rakovan@pergamon.sk']
    ADMINS = os.environ.get('ADMINS').split('~')
    GOAT = "b.rakovan@gmail.com"