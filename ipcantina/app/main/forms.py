from flask_wtf import FlaskForm
from wtforms import Field
from wtforms import SelectField,StringField, PasswordField, BooleanField, SubmitField,\
    IntegerField, FieldList, FormField, TextAreaField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Optional, Length
from app.models import User, Company
from wtforms.widgets.core import HTMLString, TextInput, SubmitInput
from markupsafe import Markup


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
    take_away = BooleanField('so sebou', default=False)


class DayMenuForm(FlaskForm):
    subfields = FieldList(FormField(MealForm), min_entries=3, max_entries=3)


class MenuForm(FlaskForm):
    fields = FieldList(FormField(DayMenuForm), min_entries=5, max_entries=5)
    submit = SubmitField('Objednať', widget=SubmitBtnWidget())


class AdminSettingsForm(FlaskForm):
    instructions = TextAreaField('Inštrukcie na úvodnej stránke', validators=[Length(min=0, max=1000)], description="Zadávanie textu podporuje HTML formát")
    price_A = FloatField('Cena A', validators=[DataRequired()])
    price_B = FloatField('Cena B', validators=[DataRequired()])
    price_C = FloatField('Cena C', validators=[DataRequired()],
                         description="Upozornenie: zmeny v cenách naberú účinnosť až v nasledujúcom týždni.")
    submit = SubmitField('Uložiť zmeny')