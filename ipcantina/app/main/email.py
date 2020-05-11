from flask import current_app, render_template
from flask_mail import Message
from app.main.utils import DateUtils
from app import mail
from app.email import send_email
from app.models import User
import os


def send_daily_summary_email(date, orderlist_fname, ordersheet_fname):
    date_str = DateUtils.to_string(date)
    subj = "[IP Cantina] Denný sumár objednávok " + date_str
    sender = current_app.config['MAIL_USERNAME']

    msg = Message(subj, sender=sender, recipients=current_app.config['ADMINS'], charset='utf-8')
    with current_app.app_context():
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

    current_app.logger.info("About to send out new menu email notifications to:")
    current_app.logger.info(str(recipients))

    for rec in recipients:
        token = rec.get_unsubscribe_token()

        send_email('[IP Cantina] Nové menu',
                   sender=current_app.config['MAIL_USERNAME'],
                   recipients=[rec.email],
                   text_body=render_template('email/menu_notification.txt',
                                             date=date_str, token=token),
                   html_body=render_template('email/menu_notification.html',
                                             date=date_str, token=token))