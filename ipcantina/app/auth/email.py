from app.email import send_email
from flask import render_template, current_app


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    current_app.logger.info("Passsword reset mail requested.")
    send_email('[IP Cantina] Obnovenie hesla',
               sender=current_app.config['MAIL_USERNAME'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

