from flask import render_template
from flask_mail import Message
from app import mail, app
from threading import Thread
from app.utils import DateUtils
from datetime import date, timedelta
from app import db
from app.models import User
import os


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    app.logger.info("Pswrd request mail requested.")
    send_email('[IP Cantina] Obnovenie hesla',
               sender=app.config['MAIL_USERNAME'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


def send_daily_summary_email(date, orderlist_fname, ordersheet_fname):
    date_str = DateUtils.to_string(date)
    subj = "[IP Cantina] Denný sumár objednávok " + date_str
    sender = app.config['MAIL_USERNAME']

    msg = Message(subj, sender=sender, recipients=app.config['ADMINS'], charset='utf-8')
    with app.app_context():
        msg.body = render_template('email/daily_summary.txt', date=date_str)
        msg.html = render_template('email/daily_summary.html', date=date_str)

        with open(orderlist_fname, "r", encoding='utf-8') as fp:
            msg.attach(os.path.basename(orderlist_fname), "text/plain", fp.read().encode('utf-8'))

        with open(ordersheet_fname, "rb") as fp:
            # bytes = fp.read().decode('utf-8')
            bytes = fp.read()
            msg.attach(os.path.basename(ordersheet_fname), "application/vnd.ms-excel", bytes)

        mail.send(msg)


def send_menu_notification_email():
    date_str = DateUtils.monday_to_friday_str()

    # recipients = User.query.filter(User.email_subscription is True).with_entities(User.email).all()
    recipients = User.query.filter(User.email_subscription == True).all()

    app.logger.info("About to send out new menu email notifications to:")
    app.logger.info(str(recipients))

    for rec in recipients:
        token = rec.get_unsubscribe_token()

        send_email('[IP Cantina] Nové menu',
                   sender=app.config['MAIL_USERNAME'],
                   recipients=[rec.email],
                   text_body=render_template('email/menu_notification.txt',
                                             date=date_str, token=token),
                   html_body=render_template('email/menu_notification.html',
                                             date=date_str, token=token))