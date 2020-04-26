from app import db, app
from werkzeug.security import generate_password_hash, check_password_hash
from app import login_manager
from flask_login import UserMixin
from datetime import datetime, timedelta
from sqlalchemy import func
import jwt
from time import time
from app.utils import DateUtils
from datetime import date


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True)
    weekday = db.Column(db.Integer)
    label = db.Column(db.String(1))
    description = db.Column(db.String(128))
    price = db.Column(db.Float(precision=2))

    def __repr__(self):
        return '<Meal {}: date {}, {} {}>'.format(self.id, self.date, DateUtils.svk_from_int(self.weekday), self.label)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    take_away = db.Column(db.Boolean)
    # week too?

    def __repr__(self):
        return '<Order {}: user {}, meal {}>'.format(self.id, self.user_id, self.meal_id)

    # @classmethod
    # def get_orders_for_today(cls):
    #     today = date.today()
    #     return cls.get_orders_for_day(today)

    @classmethod
    def get_orders_for_day(cls, date):
        meal_ids = Meal.query.with_entities(Meal.id).filter(Meal.date == date).all()
        ids = [x[0] for x in meal_ids]
        return cls.query.filter(Order.meal_id.in_(ids))


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_title = db.Column(db.String(128), unique=True)
    title = db.Column(db.String(128), unique=True)
    CRN = db.Column(db.Integer, unique=True)
    building = db.Column(db.String(3))
    token = db.Column(db.String(16))
    employees = db.relationship('User', backref='company', lazy='dynamic')

    def __repr__(self):
        return '<Company {}>'.format(self.title)


    def set_default_token(self):
        self.token = self.building + str(self.CRN)[:4]

    def check_token(self, token):
        return self.token == token

    @classmethod
    def get_list(cls):
        return cls.query.with_entities(cls.title).order_by(cls.title).all()


class UserRole:
    ADMIN = 'ADMIN'
    BASIC = 'BASIC'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    password_hash = db.Column(db.String(128))
    phone = db.Column(db.String(16))
    orders = db.relationship('Order', backref='customer', lazy='dynamic', cascade="all,delete")
    urole = db.Column(db.String(32))

    def __repr__(self):
        return '<User {}>'.format(self.first_name + " " + self.surname)

    def set_urole(self, role):
        self.urole = role

    def get_urole(self):
        return self.urole

    def is_admin(self):
        return self.urole == UserRole.ADMIN

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_orders_summary(self):
        orders = [list() for _ in range(5)]
        total_price = 0
        for meal_id, amount in Order.query.filter_by(user_id = self.id).with_entities(
                Order.meal_id, func.count()).group_by(Order.meal_id).all():
            meal = Meal.query.get(meal_id)
            if meal.date >= DateUtils.affected_week_monday():
                orders[meal.weekday].append({'meal': meal, 'amount': amount, 'cancellable': (not DateUtils.deadline_passed(meal.date)) })
                total_price += meal.price * amount

        return orders, total_price

    def get_reset_password_token(self, expires_in=600): # mins
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')  # decode cause else bytes

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)



