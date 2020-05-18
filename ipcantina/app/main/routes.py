from flask import flash, redirect, url_for, request, abort, render_template
from app import login_manager
from flask_login import current_user
from app.models import Order, UserRole, Meal
from app.main.forms import *
import json
import os
from app import db
from app.main import bp
from flask import current_app
from app.main.menu import MenuUtils
from app.main.utils import DateUtils, allowed_file
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import timedelta
from app.main.email import send_menu_notification_email


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
# todo jobs run twice: still??
# todo odstranit reg. kod?

@bp.before_app_first_request
def activate_job():
    def run_periodic_jobs(application):
        from apscheduler.schedulers.background import BackgroundScheduler
        from app.main.jobs import send_daily_summary
        from datetime import datetime, date, time
        today = date.today()
        at = time(hour=current_app.config['ORDER_DEADLINE_HOUR'])
        # at = time(hour=18, minute=41)
        start = datetime.combine(today, at)
        # start = datetime.combine(today, time(hour=23, minute=27))
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=lambda: send_daily_summary(application), trigger="interval", days=1, start_date=start)
        scheduler.start()
        current_app.logger.info("Started scheduler")

    run_periodic_jobs(current_app._get_current_object())


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
    path = current_app.config['INSTRUCTIONS_TEXT_PATH']
    with open(path, 'r', encoding='utf-8') as f:
        instructions = ' '.join(f.readlines())
        return instructions.strip()

def save_instructions(text):
    path = current_app.config['INSTRUCTIONS_TEXT_PATH']
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def update_prices(a, b, c):
    path = current_app.config['DEFAULT_PRICES_PATH']
    prices = {'A' : a, 'B': b, 'C': c}
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(prices, f, indent=4)


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    # menu = from_json(app.config['MENU_JSON_PATH'])
    menu = MenuUtils.load_from_db()
    form = MenuForm()
    # passed_days = get_num_passed_days()
    if form.validate_on_submit():
        if current_user.is_anonymous:
            return redirect(url_for('auth.login', next=request.url))
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
            return redirect(url_for('main.index'))

        db.session.commit()
        flash("Vaša objednávka bola úspešne vykonaná.", category='success')
        return redirect(url_for('main.index'))
    # else:
    #     print(form.fields.errors)
    return render_template('index.html', title='Domov', instructions=load_instructions(),
                           menu=menu, form=form, utils=DateUtils())


@bp.route('/orders', methods=['GET', 'POST'])
@login_required()
def orders():
    if request.method == 'POST':
        meal_id = request.form['meal_id']
        # unique id for each week's meals
        meal = Meal.query.get(meal_id)
        if DateUtils.deadline_passed(meal.date):
            flash("Ospravedlňujeme sa, ale každá objednávka sa dá zrušiť iba do {}-tej hodiny predošlého pracovného dňa."
                  .format(current_app.config['ORDER_DEADLINE_HOUR']), category='danger')
            return redirect(url_for('main.orders'))

        Order.query.filter(Order.user_id == current_user.id, Order.meal_id == meal_id).delete()
        db.session.commit()
        return redirect(url_for('main.orders'))
    orders, price = current_user.get_orders_summary()
    return render_template('orders.html', title='Objednávky', orders=orders, price=price, days=DateUtils())


@bp.route('/admins', methods=['GET', 'POST'])
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
                return redirect(url_for('main.admin'))
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if not file or file.filename == '':
                flash("Nebol vybraný žiaden súbor.", category='danger')
                return redirect(url_for('main.admin'))
            if not allowed_file(file.filename):
                flash("Súbor má nesprávny formát. Uistite sa, že ste nahrali excelovskú tabuľku.", category='danger')
                return redirect(url_for('main.admin'))

            filename = secure_filename(file.filename)
            path = os.path.join(current_app.config['MENU_UPLOAD_FOLDER'], filename)
            file.save(path)
            try:
                MenuUtils.save_from_excel(path, current_app.config['MENU_JSON_PATH'])
            except Exception as e:
                flash("Nahraný súbor má nesprávnu formu: {}".format(e), category='danger')
                return redirect(url_for('main.admin'))

            if update_meal_db():
                flash("Menu pre daný týždeň už bolo v minulosti nahrané, neberú sa do úvahy zmeny v cenách jedál.",
                      category='info')
            else:
                current_app.logger.info("Going go send menu update email.")
                send_menu_notification_email()

            flash("Súbor {} bol úspešne spracovaný. Prosím skontrolujte zmeny v menu na stránke.".format(file.filename), category='success')

            return redirect(url_for('main.admin'))

        else:
            if form.validate_on_submit():
                text = form.instructions.data
                save_instructions(text)
                price_A = round(form.price_A.data, 2)
                price_B = round(form.price_B.data, 2)
                price_C = round(form.price_C.data, 2)
                update_prices(price_A, price_B, price_C)

                flash("Zmeny boli úspešne uložené.", category='success')
            return redirect(url_for('main.admin'))



def update_meal_db():
    menu = MenuUtils.from_json(current_app.config['MENU_JSON_PATH'])
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
            else:
                m = Meal(date=date, weekday=date.weekday(), label=meal['label'], portion=meal['portion'],
                         description=meal['description'], allergens=meal['allergens'], price=meal['price'])
                db.session.add(m)
    db.session.commit()

    return updating


@bp.route('/unsubscribe/<token>')
def unsubscribe(token):
    user = User.verify_unsubscribe_token(token)
    if not user:
        return abort(404)

    user.email_subscription = False
    db.session.commit()
    return render_template('unsubscribe.html', title='Odber')

