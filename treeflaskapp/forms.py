from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, TextAreaField, HiddenField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional
from flask_wtf.file import FileAllowed

from datetime import datetime

from .models import *

class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self, user_language='en', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_language = user_language
        self.username.label.text = self.translate('Username')
        self.password.label.text = self.translate('Password')
        self.submit.label.text = self.translate('Submit')

    def translate(self, text):
        translations = {
            'en': {'Username': 'Username', 'Password': 'Password', 'Submit': 'Submit', 'This field is required.': 'This field is required.'},
            'ru': {'Username': 'Имя пользователя', 'Password': 'Пароль', 'Submit': 'Отправить', 'This field is required.': 'Это поле обязательно для заполнения.'}
        }
        return translations.get(self.user_language, {}).get(text, text)

# TODO: 'This field is required.' in flash both languages message handler (currently only EN)
class RegisterForm(FlaskForm):
    first_name = StringField(validators=[DataRequired()])
    last_name = StringField(validators=[DataRequired()])
    date_of_birth = DateField(format='%Y-%m-%d')
    username = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    confirm_password = PasswordField(validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField()

    def __init__(self, user_language='en', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_language = user_language
        self.first_name.label.text = self.translate('First Name')
        self.last_name.label.text = self.translate('Last Name')
        self.date_of_birth.label.text = self.translate('Date of Birth')
        self.username.label.text = self.translate('Username')
        self.email.label.text = self.translate('Email')
        self.password.label.text = self.translate('Password')
        self.confirm_password.label.text = self.translate('Confirm Password')
        self.submit.label.text = self.translate('Register')

    def translate(self, text):
        translations = {
            'en': {'First Name': 'First Name',
                   'Last Name': 'Last Name',
                   'Date of Birth': 'Date of Birth',
                   'Username': 'Username',
                   'Email': 'Email',
                   'Password': 'Password',
                   "Confirm Password": "Confirm Password",
                   "Register": "Register",
                   "Username already in use. Please log in instead.":
                       "Username already in use. Please log in instead.",
                   "Email already in use. Please log in instead.":
                       "Email already in use. Please log in instead.",
                   "This field is required.": "This field is required.",
                   "Invalid email address.": "Invalid email address.",
                   "Passwords must match.": "Passwords must match."},
            'ru': {'First Name': 'Имя',
                   'Last Name': 'Фамилия',
                   'Date of Birth': 'Дата рождения',
                   'Username': 'Имя пользователя',
                   'Email': 'Эл. адрес',
                   'Password': 'Пароль',
                   "Confirm Password": "Подтвердите пароль",
                   "Register": "Зарегистрироваться",
                   "Username already in use. Please log in instead.":
                       "Имя пользователя уже используется. Пожалуйста, войдите в систему.",
                   "Email already in use. Please log in instead.":
                       "Электронная почта уже используется. Пожалуйста, войдите в систему.",
                   "This field is required.": "Это поле обязательно для заполнения.",
                   "Invalid email address.": "Неверный адрес электронной почты.",
                   "Passwords must match.": "Пароли должны совпадать."}
        }
        return translations.get(self.user_language, {}).get(text, text)

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(self.translate('Username already in use. Please log in instead.'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(self.translate('Email already in use. Please log in instead.'))


class PersonForm(FlaskForm):
    id = HiddenField()
    name = StringField(validators=[DataRequired()])
    birth_date = DateField(format='%Y-%m-%d', validators=[Optional()])
    death_date = DateField(format='%Y-%m-%d', validators=[Optional()])
    image_file = FileField('Image File', validators=[FileAllowed(['jpg', 'png'])])
    is_alive = StringField()
    place_of_live = StringField()
    age = StringField()
    gender = StringField()
    submit = SubmitField()

    def __init__(self, user_language='en', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_language = user_language
        self.name.label.text = self.translate('Name')
        self.birth_date.label.text = self.translate('Birth Date')
        self.death_date.label.text = self.translate('Death Date')
        self.image_file.label.text = self.translate('Image File')
        self.is_alive.label.text = self.translate('Is Alive')
        self.place_of_live.label.text = self.translate('Place Of Live')
        self.age.label.text = self.translate('Age')
        self.gender.label.text = self.translate('Gender')
        self.submit.label.text = self.translate('Submit')

    def translate(self, text):
        translations = {
            'en': {'Name': 'Name', 'Birth Date': 'Birth Date', 'Death Date': 'Death Date', 'Submit': 'Submit',
                   'This field is required.': 'This field is required.', 'Image File': 'Image File', 'Is Alive': 'Is Alive',
                   'Place Of Live': 'Place Of Live', 'Age' : 'Age', 'Gender' : 'Gender'},
            'ru': {'Name': 'Имя', 'Birth Date': 'Дата рождения', 'Death Date': 'Дата смерти', 'Submit': 'Отправить',
                   'This field is required.': 'Это поле обязательно для заполнения.', 'Image File': 'Фото',
                   'Is Alive': 'Жив', 'Place Of Live': 'Место жительства', 'Age': 'Возраст', 'Gender': 'Пол'}
        }
        return translations.get(self.user_language, {}).get(text, text)

class PlaceForm(FlaskForm):
    id = HiddenField()
    name = StringField(validators=[DataRequired()])
    location = StringField()
    significance = TextAreaField()
    submit = SubmitField()

    def __init__(self, user_language='en', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_language = user_language
        self.name.label.text = self.translate('Name')
        self.location.label.text = self.translate('Location')
        self.significance.label.text = self.translate('Significance')
        self.submit.label.text = self.translate('Submit')

    def translate(self, text):
        translations = {
            'en': {'Name': 'Name', 'Location': 'Location', 'Significance': 'Significance', 'Submit': 'Submit', 'This field is required.': 'This field is required.'},
            'ru': {'Name': 'Имя', 'Location': 'Местоположение', 'Significance': 'Значение', 'Submit': 'Отправить', 'This field is required.': 'Это поле обязательно для заполнения.'}
        }
        return translations.get(self.user_language, {}).get(text, text)

class EventForm(FlaskForm):
    id = HiddenField()
    name = StringField(validators=[DataRequired()])
    date = DateField(format='%Y-%m-%d')
    submit = SubmitField()

    def __init__(self, user_language='en', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_language = user_language
        self.name.label.text = self.translate('Name')
        self.date.label.text = self.translate('Date')
        self.submit.label.text = self.translate('Submit')

    def translate(self, text):
        translations = {
            'en': {'Name': 'Name', 'Date': 'Date', 'Submit': 'Submit', 'This field is required.': 'This field is required.'},
            'ru': {'Name': 'Имя', 'Date': 'Дата', 'Submit': 'Отправить', 'This field is required.': 'Это поле обязательно для заполнения.'}
        }
        return translations.get(self.user_language, {}).get(text, text)
