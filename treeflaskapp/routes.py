from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from flask import flash, session, g
import logging
import os
from werkzeug.utils import secure_filename

from treeflaskapp import app, db, login_manager
from treeflaskapp.models import *
from treeflaskapp.forms import *


# Create a logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# Check if the directory exists, and if not, create it
log_dir = 'log_dir'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create file handler which logs even debug messages
fh = logging.FileHandler(os.path.join(log_dir, 'my_app.log'))
fh.setLevel(logging.DEBUG)

# Create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def before_request():
    g.user_language = session.get('user_language', 'en')

@app.route('/set_language/<language>')
def set_language(language):
    if language in ['en', 'ru']:
        session['user_language'] = language
    # Redirect to the referring page, or to the index if no referrer is set
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(user_language=g.user_language)
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data, date_of_birth=form.date_of_birth.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash_message = 'Registration successful. Please log in.' if g.user_language == 'en' else 'Регистрация прошла успешно. Пожалуйста, войдите в систему.'
            flash(flash_message, 'success')
            logger.info('User registered successfully')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash_message = 'An error occurred during registration: {}'.format(e) if g.user_language == 'en' else 'Во время регистрации произошла ошибка: {}'.format(e)
            flash(flash_message, 'error')
            logger.error('An error occurred during registration: {}'.format(e))
    return render_template('register.html', form=form)

# TODO: Fix
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(user_language=g.user_language)
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).first()
            if user is not None and user.check_password(form.password.data):
                login_user(user)
                session['username'] = user.username  # store the username in session
                logger.info('User logged in successfully')
                return redirect(url_for('user_profile', username=user.username))  # redirect to user's profile
            else:
                flash_message = 'Incorrect username or password. Please try again.' if g.user_language == 'en' else 'Неверное имя пользователя или пароль. Пожалуйста, попробуйте еще раз.'
                flash(flash_message)
        except Exception as e:
            logger.error(f'An error occurred during login: {e}')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    try:
        logout_user()
        session.pop('username', None)  # clear the username from session
        logger.info('User logged out successfully')
    except Exception as e:
        logger.error(f'An error occurred during logout: {e}')
    return redirect(url_for('index'))  # redirect to the index page

@app.route('/user/<username>')
@login_required
def user_profile(username):
    user = None
    try:
        user = User.query.filter_by(username=username).first_or_404()
        logger.info('User profile accessed successfully')
    except NotFound:
        logger.error(f'User {username} not found')
        flash('User not found', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f'An error occurred while accessing user profile: {e}')
    return render_template('user_profile.html', user=user, user_language=g.user_language)

