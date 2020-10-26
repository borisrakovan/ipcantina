from flask import flash, redirect, url_for, request, abort, render_template
from app import login_manager
from flask_login import current_user
from app.main.forms import *
import json
import os
from app.main import bp
from flask import current_app
from app.main.menu import MenuUtils
from app.main.persist import save_settings, load_settings
from app.main.utils import allowed_file
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import timedelta
from app.main.email import send_menu_notification_email

# from app.models import Order, UserRole, Meal
from db.models import Order, UserRole, Meal, User
from db.database import session
from db.utils import DateUtils
from db.config import config


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
            for j, dish in enumerate(field.subfields):  # label
                amount = dish.amount.data
                if not amount:
                    continue
                meal = menu[i]['meals'][j]
                if DateUtils.deadline_passed(meal.date):
                    break
                for _ in range(amount):
                    order = Order(meal_id=meal.id, customer=current_user, take_away=dish.take_away.data)
                    num_orders += 1
                    session.add(order)
        if num_orders == 0:
            flash("Nebolo vybrané žiadne jedlo.", category='danger')
            return redirect(url_for('main.index'))

        session.commit()
        flash("Vaša objednávka bola úspešne vykonaná.", category='info')
        return redirect(url_for('main.index'))

    settings = load_settings()
    return render_template('index.html', title='Domov', settings=settings,
                           menu=menu, form=form, utils=DateUtils())


@bp.route('/orders', methods=['GET', 'POST'])
@login_required()
def orders():
    if request.method == 'POST':
        meal_id = request.form['meal_id']
        take_away = request.form['take_away'] == 'True'

        # unique id for each week's meals
        meal = Meal.query.get(meal_id)
        if DateUtils.deadline_passed(meal.date):
            flash(
                "Ospravedlňujeme sa, ale každá objednávka sa dá zrušiť iba do {}-tej hodiny predošlého pracovného dňa."
                .format(config['ORDER_DEADLINE_HOUR']), category='danger')
            return redirect(url_for('main.orders'))

        Order.query.filter(
            Order.user_id == current_user.id, Order.meal_id == meal_id, Order.take_away == take_away).delete()
        session.commit()
        flash("Objednávka bola úspešne zrušená.", category="info")
        return redirect(url_for('main.orders'))

    orders_summary = Order.get_user_orders_summary(current_user, current_app.config['ORDERLIST_NUM_WEEKS'])

    view = request.args.get('view', 1)  # todo maybe

    return render_template('orders.html', title='Objednávky', summary=orders_summary, utils=DateUtils())


@bp.route('/admin', methods=['GET', 'POST'])
@login_required(role=UserRole.ADMIN)
def admin():
    form = AdminSettingsForm()
    settings = load_settings(raw_instructions=True)
    if request.method == 'GET':
        form.instructions.data = settings["instructions"]
        form.closed.data = settings["closed"]
        form.price_A.data = settings['price_A']
        form.price_B.data = settings['price_B']
        form.price_C.data = settings['price_C']
        orders_summary = Order.get_orders_summary(current_app.config['ORDERLIST_NUM_WEEKS'])
        return render_template('admin.html', title='Admin', form=form, users=User.query.all(),
                               summary=orders_summary, utils=DateUtils())

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
            settings["closed"] = False
            save_settings(settings)
            flash("Súbor {} bol úspešne spracovaný. Prosím skontrolujte zmeny v menu na stránke.".format(file.filename),
                  category='info')

            return redirect(url_for('main.admin'))

        else:
            if form.validate_on_submit():
                settings["instructions"] = form.instructions.data
                settings["closed"] = form.closed.data
                settings["price_A"] = round(form.price_A.data, 2)
                settings["price_B"] = round(form.price_B.data, 2)
                settings["price_C"] = round(form.price_C.data, 2)
                save_settings(settings)

                flash("Zmeny boli úspešne uložené.", category='info')
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
                soup = Meal(date=date, weekday=date.weekday(), label='S', portion=daily_menu['soup']['portion'],
                            description=daily_menu['soup']['description'], allergens=daily_menu['soup']['allergens'],
                            price=0.)
                # soup = Meal(week=week, day=i, label='S', description=daily_menu['soup'])
                session.add(soup)

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
                session.add(m)
    session.commit()

    return updating


@bp.route('/unsubscribe/<token>')
def unsubscribe(token):
    user = User.verify_unsubscribe_token(token)
    if not user:
        return abort(404)

    user.email_subscription = False
    session.commit()
    return render_template('unsubscribe.html', title='Odber')
