import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '43e654d66f4e46b1b4de27e2416e8c30'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                                'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']

    INSTRUCTIONS_TEXT_PATH = os.environ.get('INSTRUCTIONS_TEXT_PATH') or "index_instructions.txt"
    DEFAULT_PRICES_PATH = os.environ.get('DEFAULT_PRICES_PATH') or "prices.json"
    ATTACHMENTS_DIR_PATH = os.environ.get('ATTACHMENTS_DIR_PATH') \
                           or "C:\\Users\\brako\\Desktop\\Work\\pergamon\\ip\\ipcantina\\files\\attachments"
    MENU_UPLOAD_FOLDER = os.environ.get('MENU_UPLOAD_FOLDER') \
                         or "C:\\Users\\brako\\Desktop\\Work\\pergamon\\ip\\ipcantina\\files\\uploads"
    MENU_JSON_PATH = os.environ.get('MENU_JSON_PATH') or "menu.json"

    ORDER_DEADLINE_HOUR = os.environ.get('ORDER_DEADLINE_HOUR') or 15

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or "mail.ipdevelopment.sk"
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None # todo sure?
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or "info@ipdevelopment.sk"
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or "abcdIP!"
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or "ipadmin@centrum.sk"
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or "ipdevelopment"
    MAIL_ASCII_ATTACHMENTS = True
    # ADMINS = ['b.rakovan@gmail.com']
    ADMINS = ['b.rakovan@gmail.com', 'p.skoda@ipdevelopment.sk']
