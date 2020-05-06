from flask_wtf import FlaskForm
from wtforms import Field
from wtforms import SelectField,StringField, PasswordField, BooleanField, SubmitField,\
    IntegerField, FieldList, FormField, TextAreaField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Optional, Length
from app.models import User, Company
from wtforms.widgets.core import HTMLString, TextInput, SubmitInput
from markupsafe import Markup



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    remember_me = BooleanField('Zapamätať si ma')
    submit = SubmitField('Prihlásiť sa')

class FieldWithDescriptionWidget(TextInput):
    def __init__(self):
        super(FieldWithDescriptionWidget, self).__init__()

    def __call__(self, field, **kwargs):
        markup = Markup("<div id='token-help' style='margin-top:5px;'><em>Ak ste od svojej firmy neobdržali registračný kód alebo nie ste"
                                    " zamestnancom firmy IP Centra, pre pridelenie kódu nás prosím <a href='contact'>kontaktujte</a>.</em></div>")
        return super(FieldWithDescriptionWidget, self).__call__(field, **kwargs) + markup


class RegistrationForm(FlaskForm):
    first_name = StringField('Meno *', validators=[DataRequired()])
    surname = StringField('Priezvisko *', validators=[DataRequired()])
    email = StringField('Email *', validators=[DataRequired(), Email()])
    phone = StringField('Telefónne číslo *', validators=[DataRequired()])
    company = SelectField('Firma *', validators=[DataRequired()], coerce=int)
    token = StringField('Registračný kód *', validators=[DataRequired()], widget=FieldWithDescriptionWidget())
    password = PasswordField('Heslo *', validators=[DataRequired(), Length(8)])
    password2 = PasswordField('Heslo znova *', validators=[DataRequired(), EqualTo('password')])
    email_subscription = BooleanField('Prajem si dostávať emailové upozornenia pri zverejnení menu na nasledujúci týždeň',
                                      default="checked")
    submit = SubmitField('Zaregistrovať sa')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        other = Company.query.filter(Company.title == 'Iná').first()
        self.company.choices = [(other.id, other.title)] + [(c.id, c.title) for c in Company.query.filter(Company.title != 'Iná').order_by(
            Company.title).all()]

    def validate_email(self, email): # automatically evaluated by wtforms
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError("Email {} už je obsadený. Prosím použite iný.".format(self.email.data))

    def validate_phone(self, field):
        if len(field.data) > 16:
            raise ValidationError('Neplatné telefónne číslo.')
        phone_num = field.data.replace(' ', '').replace('+', '')
        if not phone_num.isnumeric():
            raise ValidationError('Neplatné telefónne číslo.')


class IncrementorWidget(TextInput):
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("type", self.input_type)
        if "value" not in kwargs:
            kwargs["value"] = field._value()
        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True
        return Markup('<div class="incrementor"><span class="minus">-</span><input %s><span class="plus">+</span></div>' % self.html_params(name=field.name, **kwargs))


class SubmitBtnWidget(SubmitInput):
    def __init__(self):
        super(SubmitBtnWidget, self).__init__()

    def __call__(self, field, **kwargs):
        c = kwargs.pop('class', '') or kwargs.pop('class_', '')
        kwargs['class'] = u'%s %s' % ('btn btn-default', c)
        return super(SubmitBtnWidget, self).__call__(field, **kwargs)


class MealForm(FlaskForm):
    amount = IntegerField(default=0, validators=[Optional()], widget=IncrementorWidget())
    take_away = BooleanField('so sebou', default=True)


class DayMenuForm(FlaskForm):
    subfields = FieldList(FormField(MealForm), min_entries=3, max_entries=3)


class MenuForm(FlaskForm):
    fields = FieldList(FormField(DayMenuForm), min_entries=5, max_entries=5)
    submit = SubmitField('Objednať', widget=SubmitBtnWidget())



class AccountForm(FlaskForm):
    first_name = StringField('Meno', validators=[DataRequired()])
    surname = StringField('Priezvisko', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Telefónne číslo', validators=[DataRequired()])
    company = StringField('Firma', validators=[DataRequired()])

class EditProfileForm(AccountForm):
    company = None
    submit = SubmitField('Uložiť')

    def __init__(self, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data != self.original_email:
            email = User.query.filter_by(email=email.data).first()
            if email is not None:
                raise ValidationError("Email {} už je obsadený. Prosím použite iný.".format(self.email.data))


    def validate_phone(self, field):
        if len(field.data) > 16:
            raise ValidationError('Neplatné telefónne číslo.')
        phone_num = field.data.replace(' ', '').replace('+', '')
        if not phone_num.isnumeric():
            raise ValidationError('Neplatné telefónne číslo.')


class EmailSubscriptionForm(FlaskForm):
    email_subscription = BooleanField('Prajem si dostávať emailové upozornenia pri zverejnení menu na nasledujúci týždeň')
    submit = SubmitField('Uložiť')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email *', validators=[DataRequired(), Email()])
    submit = SubmitField('Obnoviť heslo')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Heslo *', validators=[DataRequired(), Length(8)])
    password2 = PasswordField('Heslo znova *', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Zmeniť heslo')


class ChangePasswordForm(FlaskForm):
    password = PasswordField('Staré heslo *', validators=[DataRequired()])
    new_password = PasswordField('Nové heslo *', validators=[DataRequired(),  Length(8)])
    new_password2 = PasswordField('Nové heslo znova *', validators=[DataRequired(), EqualTo('new_password')])

    submit = SubmitField('Zmeniť heslo')


class DeleteAccountForm(FlaskForm):
    password = PasswordField('Heslo *', validators=[DataRequired()])
    submit = SubmitField('Vymazať')


class NotificationForm(FlaskForm):
    confirm_order = BooleanField('Prajem si dostávať emailové notifikácie pri úspešnej objednávke')
    cancel_order = BooleanField('Prajem si dostávať emailové notifikácie pri zrušení objednávky')

    submit = SubmitField('Uložiť zmeny')


class AdminSettingsForm(FlaskForm):
    instructions = TextAreaField('Inštrukcie na úvodnej stránke', validators=[Length(min=0, max=1000)], description="Zadávanie textu podporuje HTML formát")
    price_A = FloatField('Cena A', validators=[DataRequired()])
    price_B = FloatField('Cena B', validators=[DataRequired()])
    price_C = FloatField('Cena C', validators=[DataRequired()],
                         description="Upozornenie: zmeny v cenách naberú účinnosť až v nasledujúcom týždni.")
    submit = SubmitField('Uložiť zmeny')