from flask_wtf import FlaskForm
from wtforms import SelectField,StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
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
    # TODO temporarily disabled
    # token = StringField('Registračný kód *', validators=[DataRequired()], widget=FieldWithDescriptionWidget())
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


class DeleteAccountForm(FlaskForm):
    password = PasswordField('Heslo *', validators=[DataRequired()])
    submit = SubmitField('Vymazať')

