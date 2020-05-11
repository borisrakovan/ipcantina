from app import db
from app.auth import bp
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, UserRole, Company
from app.auth.forms import *
from app.auth.email import *
from werkzeug.urls import url_parse


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: # user is logged in yet accesses the /login
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Neplatná kombinácia emailu a hesla", category='danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        # 2nd condition: defence against an attacker trying to
        # redirect to some other (absolute) domain
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template('login.html', title='Prihlásenie', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    flash("Boli ste úspešne odhlásený.", category='info')
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        phone = form.phone.data.replace(' ', '')
        c = Company.query.get(form.company.data)

        if not c.check_token(form.token.data.strip()):
            flash("Neplatný registračný kód. Prosím kontaktujte vedenie Vašej firmy ohľadom poskytnutia platného kódu.",
                  category='danger')
            return redirect(url_for('auth.register'))
        # noinspection PyArgumentList
        u = User(first_name=form.first_name.data, surname=form.surname.data,
                 email=form.email.data, phone=phone, company=c, email_subscription=form.email_subscription.data)
        u.set_password(form.password.data)
        u.set_urole(UserRole.BASIC)

        db.session.add(u)
        db.session.commit()
        flash("Registrácia prebehla úspešne!", category='info')
        return redirect(url_for('auth.login'))

    return render_template('register.html', title='Registrácia', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            current_app.logger.info("User {} has requested a password request.".format(user))
            send_password_reset_email(user)
            current_app.logger.info("Email was sent successfully.".format(user))
        flash("Ďalšie inštrukcie vám boli zaslané na mailovú adresu.", category='info')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html',
                           title='Obnova hesla', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Vaše heslo bolo úspešne zmenené.', category='info')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)


@bp.route('/change_password', methods=['GET', 'POST'])
@login_required # TODO TEST
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.password.data):
            flash("Zadali ste nesprávne heslo.", category='danger')
            return redirect(url_for('auth.change_password'))
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Vaše heslo bolo úspešne zmenené.', category='info')
        return redirect(url_for('auth.account'))
    return render_template('change_password.html', title='Zmena hesla', form=form)


@bp.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.password.data):
            flash("Zadali ste nesprávne heslo.", category='danger')
            return redirect(url_for('auth.delete_account'))

        db.session.delete(current_user)
        db.session.commit()
        flash("Váš účet bol úspešne vymazaný. Ďakujeme Vám za využívanie našej aplikácie a budeme radi,"
              " ak sa čoskoro vrátite.", category='info')
        return redirect(url_for('auth.login'))
    return render_template('delete_account.html', title='Zruši účet', form=form)


@bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = AccountForm()
    email_form = EmailSubscriptionForm()
    if request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.surname.data = current_user.surname
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.company.data = current_user.company.title
        email_form.email_subscription.data = current_user.email_subscription or False

    elif email_form.validate_on_submit():
        current_user.email_subscription = email_form.email_subscription.data
        db.session.commit()
        flash('Vaše zmeny boli úspešne uložené.', category='info')
        return redirect(url_for('auth.account'))
    return render_template('account.html', title='Účet', form=form, email_form=email_form)


@bp.route("/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.email)
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.surname = form.surname.data
        current_user.email = form.email.data

        current_user.phone = form.phone.data.replace(' ', '')
        # current_user.company = form.company.data
        db.session.commit()
        flash('Vaše zmeny boli úspešne uložené.', category='info')
        return redirect(url_for('auth.account'))

    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.surname.data = current_user.surname
        form.email.data = current_user.email
        form.phone.data = current_user.phone

    return render_template('edit_profile.html', title='Zmena údajov', form=form)
