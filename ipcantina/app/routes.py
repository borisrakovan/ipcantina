import os
from flask import render_template, flash, redirect, url_for, request, abort
from app import app
from app import login_manager
from flask_login import current_user, login_user, logout_user
from app.models import User, Order, UserRole, Meal, Company
from app.forms import *
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app.menu import MenuUtils
from app.utils import DateUtils, allowed_file
from functools import wraps
from app.forms import ResetPasswordRequestForm
from app.email import *
from datetime import timedelta
import json

# todo update v strede tyzdna: zatvorenie:ak maju ludia objednane na piatok a zatvori sa
#  (napr), objednavka im ostane, treba napisat mail.

#   fixme  todo v piatok by malo byt este vidiet objednavky aj na dany tyzden
#    pagination na objednavkove tyzdne if youre bored
# todo: translate flash messages
# #  feedback kontaktny formular
# todo kontrolny blok
# todo dynamicke ceny cez js v indexe
# pdf generovanie
# vyraznejsie menu
# todo some logs
# todo jobs run twice
# todo notifikacie TEST + update old users
# todo accoun subs toggle not showing flash msg


def login_required(role=UserRole.BASIC):
    def login_wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
               return login_manager.unauthorized()
            urole = current_user.get_urole()
            if urole != role and role != UserRole.BASIC:
                return login_manager.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return login_wrapper


def load_instructions():
    path = app.config['INSTRUCTIONS_TEXT_PATH']
    with open(path, 'r', encoding='utf-8') as f:
        instructions = ' '.join(f.readlines())
        return instructions.strip()

def save_instructions(text):
    path = app.config['INSTRUCTIONS_TEXT_PATH']
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def update_prices(a, b, c):
    path = app.config['DEFAULT_PRICES_PATH']
    prices = {'A' : a, 'B': b, 'C': c}
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(prices, f, indent=4)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    # menu = from_json(app.config['MENU_JSON_PATH'])
    menu = MenuUtils.load_from_db()
    form = MenuForm()
    # passed_days = get_num_passed_days()
    if form.validate_on_submit():
        if current_user.is_anonymous:
            return redirect(url_for('login', next=request.url))
        num_orders = 0
        for i, field in enumerate(form.fields):  # day
            for j, dish in enumerate(field.subfields): # label
                amount = dish.amount.data
                if not amount:
                    continue

                meal = menu[i]['meals'][j]
                if DateUtils.deadline_passed(meal.date):
                    break
                for _ in range(amount):
                    order = Order(meal_id=meal.id, customer=current_user, take_away=dish.take_away.data)
                    num_orders += 1
                    db.session.add(order)
        if num_orders == 0:
            flash("Nebolo vybrané žiadne jedlo.", category='info')
            return redirect(url_for('index'))

        db.session.commit()
        flash("Vaša objednávka bola úspešne vykonaná.", category='success')
        return redirect(url_for('index'))
    # else:
    #     print(form.fields.errors)
    return render_template('index.html', title='Domov', instructions=load_instructions(),
                           menu=menu, form=form, utils=DateUtils())


@app.route('/orders', methods=['GET', 'POST'])
@login_required()
def orders():
    if request.method == 'POST':
        meal_id = request.form['meal_id']
        # unique id for each week's meals
        meal = Meal.query.get(meal_id)
        if DateUtils.deadline_passed(meal.date):
            flash("Ospravedlňujeme sa, ale každá objednávka sa dá zrušiť iba do {}-tej hodiny predošlého pracovného dňa."
                  .format(app.config['ORDER_DEADLINE_HOUR']), category='danger')  # todo pracovneho?
            return redirect(url_for('orders'))

        Order.query.filter(Order.user_id == current_user.id, Order.meal_id == meal_id).delete()
        db.session.commit()
        return redirect(url_for('orders'))
    orders, price = current_user.get_orders_summary()
    return render_template('orders.html', title='Objednávky', orders=orders, price=price, days=DateUtils())


@app.route('/account', methods=['GET', 'POST'])
@login_required()
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
        return redirect(url_for('account'))
    return render_template('account.html', title='Účet', form=form, email_form=email_form)


@app.route("/edit_profile", methods=['GET', 'POST'])
@login_required()
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
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.surname.data = current_user.surname
        form.email.data = current_user.email
        form.phone.data = current_user.phone

    return render_template('edit_profile.html', title='Zmena údajov', form=form)


@app.route('/admins', methods=['GET', 'POST'])
@login_required(role=UserRole.ADMIN)
def admin():
    form = AdminSettingsForm()

    if request.method == 'GET':
        form.instructions.data = load_instructions()
        prices = MenuUtils.get_default_prices()
        form.price_A.data = prices['A']
        form.price_B.data = prices['B']
        form.price_C.data = prices['C']
        orders = Order.get_all_for_current_week()
        return render_template('admin.html', title='Admin', form=form, users=User.query.all(), orders=orders, days=DateUtils)

    else:
        if 'upload' in request.form:
            # check if the post request has the file part
            if 'file' not in request.files:
                flash("HTTP request neobsahuje žiaden súbor.", category='danger')
                return redirect(url_for('admin'))
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if not file or file.filename == '':
                flash("Nebol vybraný žiaden súbor.", category='danger')
                return redirect(url_for('admin'))
            if not allowed_file(file.filename):
                flash("Súbor má nesprávny formát. Uistite sa, že ste nahrali excelovskú tabuľku.", category='danger')
                return redirect(url_for('admin'))

            filename = secure_filename(file.filename)
            path = os.path.join(app.config['MENU_UPLOAD_FOLDER'], filename)
            file.save(path)
            try:
                MenuUtils.save_from_excel(path, app.config['MENU_JSON_PATH'])
            except Exception as e:
                flash("Nahraný súbor má nesprávnu formu: {}".format(e), category='danger')
                return redirect(url_for('admin'))

            if update_meal_db():
                flash("Menu pre daný týždeň už bolo v minulosti nahrané, neberú sa do úvahy zmeny v cenách jedál.",
                      category='info')
            else:
                app.logger.info("Going go send menu update email.")
                send_menu_notification_email()

            flash("Súbor {} bol úspešne spracovaný. Prosím skontrolujte zmeny v menu na stránke.".format(file.filename), category='success')

            return redirect(url_for('admin'))

        else:
            if form.validate_on_submit():
                text = form.instructions.data
                save_instructions(text)
                price_A = round(form.price_A.data, 2)
                price_B = round(form.price_B.data, 2)
                price_C = round(form.price_C.data, 2)
                update_prices(price_A, price_B, price_C)

                flash("Zmeny boli úspešne uložené.", category='success')
            return redirect(url_for('admin'))


def update_meal_db():
    menu = MenuUtils.from_json(app.config['MENU_JSON_PATH'])
    monday = DateUtils.affected_week_monday()
    updating = False
    for i, daily_menu in enumerate(menu):
        if not daily_menu['open']:
            continue
        date = monday + timedelta(days=i)

        # upload in the middle of a week
        if 'soup' in daily_menu:
            old_soup = Meal.query.filter(Meal.date == date, Meal.label == 'S').first()
            if old_soup is not None:
                updating = True
                old_soup.portion = daily_menu['soup']['portion']
                old_soup.description = daily_menu['soup']['description']
                old_soup.allergens = daily_menu['soup']['allergens']
            else:
                soup = Meal(date=date, weekday=date.weekday(), label='S',portion=daily_menu['soup']['portion'],
                            description=daily_menu['soup']['description'], allergens=daily_menu['soup']['allergens'], price=0.)
                # soup = Meal(week=week, day=i, label='S', description=daily_menu['soup'])
                db.session.add(soup)

        for meal in daily_menu['meals']:
            old = Meal.query.filter(Meal.date == date, Meal.label == meal['label']).first()
            if old is not None:
                updating = True
                old.portion = meal['portion']
                old.description = meal['description']
                old.allergens = meal['allergens']
                # todo possibility to update price too? NO
            else:
                m = Meal(date=date, weekday=date.weekday(), label=meal['label'], portion=meal['portion'],
                         description=meal['description'], allergens=meal['allergens'], price=meal['price'])
                db.session.add(m)
    db.session.commit()

    return updating


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: # user is logged in yet accesses the /login
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Neplatná kombinácia emailu a hesla", category='danger')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        # 2nd condition: defence against an attacker trying to
        # redirect to some other (absolute) domain
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Prihlásenie', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("Boli ste úspešne odhlásený.", category='info')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        phone = form.phone.data.replace(' ', '')
        c = Company.query.get(form.company.data)

        if not c.check_token(form.token.data.strip()):
            flash("Neplatný registračný kód. Prosím kontaktujte vedenie Vašej firmy ohľadom poskytnutia platného kódu.",
                  category='danger')
            return redirect(url_for('register'))
        # noinspection PyArgumentList
        u = User(first_name=form.first_name.data, surname=form.surname.data,
                 email=form.email.data, phone=phone, company=c, email_subscription=form.email_subscription.data)
        u.set_password(form.password.data)
        u.set_urole(UserRole.BASIC)

        db.session.add(u)
        db.session.commit()
        flash("Registrácia prebehla úspešne!", category='info')
        return redirect(url_for('login'))

    return render_template('register.html', title='Registrácia', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            app.logger.info("User {} has requested a password request.".format(user))
            send_password_reset_email(user)
            app.logger.info("Email was sent successfully.".format(user))
        flash("Ďalšie inštrukcie vám boli zaslané na mailovú adresu.", category='info')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Obnova hesla', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Vaše heslo bolo úspešne zmenené.', category='info')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/unsubscribe/<token>')
def unsubscribe(token):
    user = User.verify_unsubscribe_token(token)
    if not user:
        return abort(404)

    user.email_subscription = False
    db.session.commit()
    return render_template('unsubscribe.html')


@app.route('/change_password', methods=['GET', 'POST'])
@login_required()
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.password.data):
            flash("Zadali ste nesprávne heslo.", category='danger')
            return redirect(url_for('change_password'))
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Vaše heslo bolo úspešne zmenené.', category='info')
        return redirect(url_for('account'))
    return render_template('change_password.html', form=form)


@app.route('/delete_account', methods=['GET', 'POST'])
@login_required()
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.password.data):
            flash("Zadali ste nesprávne heslo.", category='danger')
            return redirect(url_for('delete_account'))

        # todo only deactivate?
        db.session.delete(current_user)
        db.session.commit()
        flash("Váš účet bol úspešne vymazaný. Ďakujeme Vám za využívanie našej aplikácie a budeme radi,"
              " ak sa čoskoro vrátite.", category='info')
        return redirect(url_for('login'))
    return render_template('delete_account.html', form=form)


@app.route('/gdpr')
def gdpr():
    return render_template('gdpr.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')