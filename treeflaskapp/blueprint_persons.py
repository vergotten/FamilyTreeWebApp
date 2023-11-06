# persons.py
from flask import Blueprint, request, render_template, redirect, url_for, g, flash
from flask_login import login_required, current_user
from .models import Person, db
from .forms import PersonForm
from werkzeug.utils import secure_filename
import os

persons = Blueprint('persons', __name__)

def handle_file_upload(file):
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg', 'gif', 'JPG', 'JPEG'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Get the current script's directory
        script_dir = os.path.dirname(os.path.realpath(__file__))
        # Join it with your desired relative path
        filepath = os.path.join(script_dir, 'static/uploads', filename)
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        return os.path.join('uploads', filename)  # return only the relative path

    return None

@persons.route('/user/<username>/persons')
def persons_view(username):
    try:
        if username == current_user.username:
            persons = Person.query.filter_by(user_id=current_user.id).all()
            for person in persons:
                if person.death_date is not None:
                    person.is_alive = False
                else:
                    person.is_alive = True
            db.session.commit()
            form = PersonForm(user_language=g.user_language)  # create an instance of your form
            return render_template('persons.html', persons=persons, form=form)
        else:
            return "Unauthorized", 403
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred", 500

@persons.route('/user/<username>/create_person', methods=['GET', 'POST'])
@login_required
def create_person(username):
    form = PersonForm(user_language=g.user_language)
    if form.validate_on_submit():
        try:
            filepath = None
            if 'image_file' in request.files:
                filepath = handle_file_upload(request.files['image_file'])

            birth_date = form.birth_date.data if form.birth_date.data else None
            death_date = form.death_date.data if form.death_date.data else None
            person = Person(user_id=current_user.id, name=form.name.data, birth_date=birth_date, death_date=death_date, image_file=filepath)
            db.session.add(person)
            db.session.commit()
            flash_message = 'Person created successfully!' if g.user_language == 'en' else 'Персона успешно создана!'
            flash(flash_message, 'success')
            return redirect(url_for('persons.persons_view', username=username))
        except Exception as e:
            db.session.rollback()
            flash_message = 'An error occurred while creating the person: {}'.format(e) if g.user_language == 'en' \
                else 'Произошла ошибка при создании персоны: {}'.format(e)
            flash(flash_message, 'error')
    return render_template('create_person.html', form=form, username=username)

@persons.route('/user/<username>/edit_person/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_person(username, id):
    person = Person.query.get(id)
    if person is None or person.user_id != current_user.id:
        return "Unauthorized", 403

    form = PersonForm(obj=person, user_language=g.user_language)
    if form.validate_on_submit():
        try:
            filepath = None  # Initialize filepath with a default value
            if 'image_file' in request.files:
                filepath = handle_file_upload(request.files['image_file'])
                if filepath is not None:
                    person.image_file = filepath  # update image_file field with full path
                db.session.commit()  # commit changes to the database

            person.name = form.name.data
            person.birth_date = form.birth_date.data if form.birth_date.data else None
            person.death_date = form.death_date.data if form.death_date.data else None
            db.session.commit()
            flash_message = 'Person updated successfully!' if g.user_language == 'en' else 'Персона успешно обновлена!'
            flash(flash_message, 'success')
            return redirect(url_for('persons.persons_view', username=username))
        except Exception as e:
            db.session.rollback()
            flash_message = 'An error occurred while updating the person: {}'.format(e) if g.user_language == 'en' \
                else 'Произошла ошибка при обновлении персоны: {}'.format(e)
            flash(flash_message, 'error')

    return render_template('edit_person.html', form=form, username=username, person=person)

@persons.route('/user/<username>/delete_person/<int:id>', methods=['POST'])
@login_required
def delete_person(username, id):
    person = Person.query.get(id)
    if person is None or person.user_id != current_user.id:
        return "Unauthorized", 403

    try:
        db.session.delete(person)
        db.session.commit()
        flash_message = 'Person deleted successfully!' if g.user_language == 'en' else 'Персона успешно удалена!'
        flash(flash_message, 'success')
    except Exception as e:
        db.session.rollback()
        flash_message = 'An error occurred while deleting the person: {}'.format(e) if g.user_language == 'en' \
            else 'Произошла ошибка при удалении персоны: {}'.format(e)
        flash(flash_message, 'error')

    return redirect(url_for('persons.persons_view', username=username))
