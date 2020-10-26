import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '43e654d66f4e46b1b4de27e2416e8c30'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #                             'sqlite:///' + os.path.join(basedir, 'app.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER_NAME = os.environ.get('SERVER_NAME')
    # SERVER_NAME = "cantina.ipcentrum.sk"
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']

    ATTACHMENTS_DIR_PATH = os.environ.get('ATTACHMENTS_DIR_PATH')
    MENU_UPLOAD_FOLDER = os.environ.get('MENU_UPLOAD_FOLDER')
    ORDERLIST_NUM_WEEKS = 3
    MENU_JSON_PATH = os.environ.get('MENU_JSON_PATH')
    APP_SETTINGS_PATH = os.environ.get('APP_SETTINGS_PATH')

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))

    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_ASCII_ATTACHMENTS = True

    ADMINS = os.environ.get('ADMINS').split('~')
    GOAT = "b.rakovan@gmail.com"