from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from .models import User  # replace with your actual User model

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
            'en': {'Username': 'Username', 'Password': 'Password', 'Submit': 'Submit'},
            'ru': {'Username': 'Имя пользователя', 'Password': 'Пароль', 'Submit': 'Отправить'}
        }
        return translations.get(self.user_language, {}).get(text, text)

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
                       "Email already in use. Please log in instead."},
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
                       "Электронная почта уже используется. Пожалуйста, войдите в систему."}
        }
        return translations.get(self.user_language, {}).get(text, text)

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(self.translate('Username already in use. Please log in instead.'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(self.translate('Email already in use. Please log in instead.'))
