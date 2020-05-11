from flask import render_template

from app.general import bp


@bp.route('/gdpr')
def gdpr():
   return render_template('gdpr.html', title='GDPR')


@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html', title='Kontakt')