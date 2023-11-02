from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from flask import flash, session, g
import logging
import os

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
    return render_template('user_panel.html', user=user, user_language=g.user_language)

from flask_login import current_user

@app.route('/user/<username>/persons')
def persons(username):
    if username == current_user.username:
        persons = Person.query.filter_by(user_id=current_user.id).all()
        form = PersonForm(user_language=g.user_language)  # create an instance of your form
        return render_template('persons.html', persons=persons, form=form)
    else:
        return "Unauthorized", 403

@app.route('/user/<username>/create_person', methods=['GET', 'POST'])
@login_required
def create_person(username):
    form = PersonForm(user_language=g.user_language)
    logger.debug('PersonForm created')
    if form.validate_on_submit():
        try:
            birth_date = form.birth_date.data if form.birth_date.data else None
            death_date = form.death_date.data if form.death_date.data else None
            person = Person(user_id=current_user.id, name=form.name.data, birth_date=birth_date, death_date=death_date)
            db.session.add(person)
            db.session.commit()
            # flash_message = 'Person created successfully!' if g.user_language == 'en' else 'Человек успешно создан!'
            # flash(flash_message, 'success')
            logger.debug('Person created successfully')
            return redirect(url_for('persons', username=username))
        except Exception as e:
            db.session.rollback()
            flash_message = 'An error occurred while creating the person: {}'.format(e) if g.user_language == 'en' else 'Произошла ошибка при создании человека: {}'.format(e)
            flash(flash_message, 'error')
            logger.error('An error occurred: {}'.format(e))
            print("errors: ", form.errors)
    return render_template('create_person.html', form=form, username=username)

@app.route('/user/<username>/edit_person/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_person(username, id):
    try:
        person = Person.query.get(id)
    except Exception as e:
        flash('An error occurred while fetching the person: {}'.format(e), 'error')
        return redirect(url_for('persons', username=username))  # Redirect to a safe page

    if person is None:
        abort(404)  # Not found

    form = PersonForm(obj=person)
    if form.validate_on_submit():
        try:
            person.name = form.name.data
            person.birth_date = form.birth_date.data if form.birth_date.data else None
            person.death_date = form.death_date.data if form.death_date.data else None
            db.session.commit()
            flash('Person updated successfully!', 'success')
            return redirect(url_for('persons', username=username))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the person: {}'.format(e), 'error')

    return render_template('edit_person.html', form=form, username=username, person=person)

@app.route('/user/<username>/delete_person/<id>', methods=['POST'])
@login_required
def delete_person(username, id):
    person = Person.query.get(id)
    if person.user_id != current_user.id:
        abort(403)  # Forbidden
    try:
        db.session.delete(person)
        db.session.commit()
        flash_message = 'Person deleted successfully!' if g.user_language == 'en' else 'Человек успешно удален!'
        flash(flash_message, 'success')
    except Exception as e:
        db.session.rollback()
        # flash_message = 'An error occurred while deleting the person: {}'.format(e) if g.user_language == 'en' else 'Произошла ошибка при удалении человека: {}'.format(e)
        # flash(flash_message, 'error')
    return redirect(url_for('persons', username=username))

@app.route('/user/<username>/places')
def places(username):
    if username == current_user.username:
        places = Place.query.filter_by(user_id=current_user.id).all()
        form = PlaceForm(user_language=g.user_language)  # create an instance of your form
        return render_template('places.html', places=places, form=form)
    else:
        return "Unauthorized", 403

@app.route('/user/<username>/create_place', methods=['GET', 'POST'])
@login_required
def create_place(username):
    form = PlaceForm(user_language=g.user_language)
    logger.debug('PlaceForm created')
    if form.validate_on_submit():
        try:
            place = Place(user_id=current_user.id, name=form.name.data, location=form.location.data,
                          significance=form.significance.data)
            db.session.add(place)
            db.session.commit()
            flash_message = 'Place created successfully!' if g.user_language == 'en' else 'Место успешно создано!'
            flash(flash_message, 'success')
            logger.debug('Place created successfully')
            return redirect(url_for('places', username=username))
        except Exception as e:
            db.session.rollback()
            # flash_message = 'An error occurred while creating the place: {}'.format(e) if g.user_language == 'en' else 'Произошла ошибка при создании места: {}'.format(e)
            # flash(flash_message, 'error')
            logger.error('An error occurred: {}'.format(e))
            print("errors: ", form.errors)
    return render_template('create_place.html', form=form, username=username)

@app.route('/user/<username>/edit_place/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_place(username, id):
    place = Place.query.get(id)
    if place is None:
        abort(404)  # Not found
    form = PlaceForm(obj=place)
    if form.validate_on_submit():
        try:
            place.name = form.name.data
            place.location = form.location.data
            place.significance = form.significance.data
            db.session.commit()
            flash('Place updated successfully!', 'success')
            return redirect(url_for('places', username=username))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the place: {}'.format(e), 'error')
    return render_template('edit_place.html', form=form, username=username, place=place)

@app.route('/user/<username>/events')
def events(username):
    if username == current_user.username:
        events = Event.query.filter_by(user_id=current_user.id).all()
        form = EventForm(user_language=g.user_language)  # create an instance of your form
        return render_template('events.html', events=events, form=form)
    else:
        return "Unauthorized", 403

@app.route('/user/<username>/create_event', methods=['GET', 'POST'])
@login_required
def create_event(username):
    form = EventForm(user_language=g.user_language)
    logger.debug('EventForm created')
    if form.validate_on_submit():
        try:
            event = Event(user_id=current_user.id, name=form.name.data, date=form.date.data)
            db.session.add(event)
            db.session.commit()
            flash_message = 'Event created successfully!' if g.user_language == 'en' else 'Событие успешно создано!'
            flash(flash_message, 'success')
            logger.debug('Event created successfully')
            return redirect(url_for('events', username=username))
        except Exception as e:
            db.session.rollback()
            # flash_message = 'An error occurred while creating the event: {}'.format(e) if g.user_language == 'en' else 'Произошла ошибка при создании события: {}'.format(e)
            # flash(flash_message, 'error')
            logger.error('An error occurred: {}'.format(e))
            print("errors: ", form.errors)
    return render_template('create_event.html', form=form, username=username)

@app.route('/user/<username>/edit_event/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(username, id):
    event = Event.query.get(id)
    if event is None:
        abort(404)  # Not found
    form = EventForm(obj=event)
    if form.validate_on_submit():
        try:
            event.name = form.name.data
            event.date = form.date.data
            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('events', username=username))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the event: {}'.format(e), 'error')
    return render_template('edit_event.html', form=form, username=username, event=event)
