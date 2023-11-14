# persons.py
from flask import Blueprint, request, render_template, redirect, url_for, g, flash, jsonify
from flask_login import login_required, current_user
from .models import Person, Place, Event, db
from .forms import PersonForm
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from sqlalchemy import and_, or_

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
        filepath = os.path.join(script_dir, 'static/uploads', filename); print(f"filepath: {filepath}")
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        return os.path.join('uploads', filename)  # return only the relative path

    return None

def get_choices(persons, selected_person):
    if persons is not None:
        choices = [(p.id, p.name) for p in persons]
        if selected_person is not None and (selected_person.id, selected_person.name) in choices:
            choices.remove((selected_person.id, selected_person.name))
            choices.insert(0, (None, ''))
            choices.insert(0, (selected_person.id, selected_person.name))
        else:
            choices.insert(0, (None, ''))
        return choices

def get_persons(role, person):
    if person is not None:
        if role == 'spouse':
            return Person.query.filter(and_(Person.gender != person.gender, Person.id != person.id,
                                            Person.user_id == current_user.id)).order_by(Person.id).all()
        elif role == 'mother':
            return Person.query.filter(
                and_(Person.gender == 'Female', Person.id != person.id, Person.user_id == current_user.id)).order_by(
                Person.id).all()
        elif role == 'father':
            return Person.query.filter(
                and_(Person.gender == 'Male', Person.id != person.id, Person.user_id == current_user.id)).order_by(
                Person.id).all()

@persons.route('/user/<username>/persons')
def persons_view(username):
    try:
        if username == current_user.username:
            persons = Person.query.filter_by(user_id=current_user.id).all()
            for person in persons:
                if person.birth_date is not None:
                    birth_date = person.birth_date
                    today = datetime.today().date()  # Get the current date
                    age = today.year - birth_date.year

                    # if birthday hasn't happened this year, subtract 1
                    if (today.month, today.day) < (birth_date.month, birth_date.day):
                        age -= 1
                    person.age = age
                else:
                    person.age = None

                if person.death_date is not None:
                    person.is_alive = False
                    death_date = person.death_date
                    age_at_death = death_date.year - birth_date.year
                    if (death_date.month, death_date.day) < (birth_date.month, birth_date.day):
                        age_at_death -= 1
                    person.age = age_at_death
                else:
                    person.is_alive = True

            db.session.commit()

            form = PersonForm(user_language=g.user_language)  # create an instance of your form
            return render_template('persons.html', persons=persons, form=form, Person=Person)
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
            filepath = handle_file_upload(request.files['image_file']) if 'image_file' in request.files and request.files['image_file'].filename != '' else None

            person = Person(
                user_id=current_user.id,
                name=form.name.data,
                is_alive=form.is_alive.data,
                place_of_live=form.place_of_live.data or None,
                place_of_birth=form.place_of_birth.data or None,
                birth_date=form.birth_date.data or None,
                death_date=form.death_date.data or None,
                image_file=filepath,
                comment=form.comment.data or None
            )

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

    # Set choices for spouse, mother, and father
    for relation in ['spouse', 'mother', 'father']:
        persons = get_persons(relation, person)
        related_person = Person.query.get(getattr(person, f"{relation}_id")) if getattr(person, f"{relation}_id") else None
        getattr(form, relation).choices = get_choices(persons, related_person)

    if form.validate_on_submit():
        try:
            filepath = handle_file_upload(request.files['image_file']) if 'image_file' in request.files and request.files['image_file'].filename != '' else None

            def set_person_attributes(person, form):
                person.name = form.name.data or None
                person.image_file = filepath or None
                person.birth_date = form.birth_date.data or None
                person.is_alive = form.is_alive.data
                person.death_date = form.death_date.data or None
                person.place_of_live = form.place_of_live.data or None
                person.place_of_birth = form.place_of_birth.data or None
                person.gender = form.gender.data or None
                person.comment = form.comment.data or None

            set_person_attributes(person, form)

            # Get the selected spouse
            selected_spouse = Person.query.get(form.spouse.data)
            person.spouse_id = selected_spouse.id if selected_spouse is not None else None

            person.mother_id = form.mother.data or None  # Save the selected mother id to the person's mother field
            person.father_id = form.father.data or None  # Save the selected father id to the person's father field

            # Check if Place of Birth already exists
            place_name = f"Place of birth. {person.name}" if g.user_language == 'en' else f"Место рождения. {person.name}"
            place_of_birth = Place.query.filter_by(user_id=current_user.id, name=place_name).first()
            if place_of_birth and form.place_of_birth.data and form.place_of_birth.data != "":
                # Update existing Place of Birth
                place_of_birth.location = form.place_of_birth.data
            elif form.place_of_birth.data and form.place_of_birth.data != "":
                # Create new Place of Birth
                place_of_birth = Place(user_id=current_user.id,
                                       name=place_name,
                                       location=form.place_of_birth.data)
                db.session.add(place_of_birth)

            # Check if Birth Event already exists
            event_name = f"Birth. {person.name}" if g.user_language == 'en' else f"Рождение. {person.name}"
            birth_event = Event.query.filter_by(user_id=current_user.id, name=event_name).first()
            if birth_event and form.birth_date.data and form.birth_date.data != "":
                # Update existing Birth Event
                birth_event.date = person.birth_date
                birth_event.place_id = place_of_birth.id
            elif form.birth_date.data and form.birth_date.data != "":
                # Create new Birth Event
                birth_event = Event(user_id=current_user.id,
                                    name=event_name,
                                    date=person.birth_date,
                                    place_id=place_of_birth.id)
                db.session.add(birth_event)

            # Check if Place of Death and Death Event already exist if person is not alive
            if not person.is_alive and form.place_of_live.data and form.place_of_live.data != "" and person.death_date:
                place_name = f"Place of death. {person.name}" if g.user_language == 'en' else f"Место смерти. {person.name}"
                place_of_death = Place.query.filter_by(user_id=current_user.id, name=place_name).first()
                if place_of_death:
                    # Update existing Place of Death
                    place_of_death.location = form.place_of_live.data
                else:
                    # Create new Place of Death
                    place_of_death = Place(user_id=current_user.id,
                                           name=place_name,
                                           location=form.place_of_live.data)
                    db.session.add(place_of_death)

                event_name = f"Death of {person.name}" if g.user_language == 'en' else f"Смерть. {person.name}"
                death_event = Event.query.filter_by(user_id=current_user.id, name=event_name).first()
                if death_event:
                    # Update existing Death Event
                    death_event.date = person.death_date
                    death_event.place_id = place_of_death.id
                else:
                    # Create new Death Event
                    death_event = Event(user_id=current_user.id,
                                        name=event_name,
                                        date=person.death_date,
                                        place_id=place_of_death.id)
                    db.session.add(death_event)

            db.session.commit()

            flash_message = 'Person, Places, and Events updated successfully!' if g.user_language == 'en' else 'Персона, места и события успешно обновлены!'
            flash(flash_message, 'success')
            return redirect(url_for('persons.persons_view', username=username))
        except Exception as e:
            db.session.rollback()
            flash_message = 'An error occurred while updating the person, places, and events: {}'.format(
                e) if g.user_language == 'en' \
                else 'Произошла ошибка при обновлении персоны, мест и событий: {}'.format(e)
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

@persons.route('/user/<username>/edit_person/<int:id>/delete-file', methods=['POST'])
@login_required
def delete_file(username, id):
    data = request.get_json()
    filename = data.get('filename')

    print('Received request:', request)  # Print the entire request
    print('Received data:', data)  # Print the received JSON data
    print('Received filename:', filename)  # Print the received filename

    if filename:
        person = Person.query.get(id)
        if person and person.image_file == filename:
            # If the person's image_file is the same as the filename, set it to None
            person.image_file = None
            db.session.commit()

            file_path = os.path.join(persons.root_path, 'static', filename)

            if os.path.exists(file_path):
                os.remove(file_path)

            return jsonify({'message': 'File deleted.'}), 200
        else:
            return jsonify({'message': 'File not found.'}), 404
    else:
        return jsonify({'message': 'No filename provided.'}), 400

@persons.route('/user/<username>/tree')
@login_required
def persons_tree(username):
    try:
        if username == current_user.username:
            persons = Person.query.filter_by(user_id=current_user.id).all()
            persons_data = []
            for person in persons:
                # Determine the parent id
                pid = None
                if person.father_id is not None:
                    pid = person.father_id
                elif person.mother_id is not None:
                    pid = person.mother_id

                # Add the person to the data
                persons_data.append({
                    'id': person.id,
                    'pid': pid,
                    'name': person.name,
                    'img': "/static/" + person.image_file if person.image_file else None,
                    'partners': [person.spouse_id] if person.spouse_id else [],
                    'extra': {
                        'age': person.age if person.age else None,
                        'is_alive': person.is_alive if person.is_alive else False,
                        'place_of_live': person.place_of_live if person.place_of_live else None,
                        'place_of_birth': person.place_of_birth if person.place_of_birth else None,
                        'gender': person.gender if person.gender else None,
                        'comment': person.comment if person.comment else None,
                        'user_id': person.user_id if person.user_id else None,
                        'birth_date': person.birth_date.strftime('%d-%m-%Y') if person.birth_date is not None else None,
                        'death_date': person.death_date.strftime('%d-%m-%Y') if person.death_date is not None else None,
                        'mother_id': person.mother_id if person.mother_id else None,
                        'father_id': person.father_id if person.father_id else None,
                    }
                })

            db.session.commit()

            return render_template('tree.html', persons=persons, Person=Person, persons_data=persons_data)
        else:
            return "Unauthorized", 403
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred", 500

