import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler,RotatingFileHandler


app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
bootstrap = Bootstrap(app)
mail = Mail(app)

# here so we don't have circular imports
# everything I code has to be imported here!
from app import routes, models, errors, forms
from app.models import User, Meal, Order, Company

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='IP Cantina Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

        # logging to file
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/ipcantina.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('IP Cantina startup')


from apscheduler.schedulers.background import BackgroundScheduler
from app.jobs import send_daily_summary
from datetime import datetime, date, time


def run_periodic_jobs():
    today = date.today()
    at = time(hour=app.config['ORDER_DEADLINE_HOUR'])
    # at = time(hour=18, minute=41)
    start = datetime.combine(today, at)
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=send_daily_summary, trigger="interval", days=1, start_date=start)
    scheduler.start()
    print("started scheduler")


run_periodic_jobs()


# # # MIGRATION # # #
# flask db stamp head
#  db migrate -m "hm";  flask db upgrade

# # # EMAILS TEST # # #
#(venv) $ python -m smtpd -n -c DebuggingServer localhost:8025
# (venv) $ set MAIL_SERVER=localhost
# (venv) $ set MAIL_PORT=8025
