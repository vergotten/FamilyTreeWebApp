# persons.py
from flask import Blueprint, request, render_template, redirect, url_for, g, flash
from flask_login import login_required, current_user
from .models import Person, db
from .forms import PersonForm

persons = Blueprint('persons', __name__)

@persons.route('/user/<username>/persons')
def persons_view(username):
    if username == current_user.username:
        persons = Person.query.filter_by(user_id=current_user.id).all()
        form = PersonForm(user_language=g.user_language)  # create an instance of your form
        return render_template('persons.html', persons=persons, form=form)
    else:
        return "Unauthorized", 403

@persons.route('/user/<username>/create_person', methods=['GET', 'POST'])
@login_required
def create_person(username):
    form = PersonForm(user_language=g.user_language)
    if form.validate_on_submit():
        try:
            birth_date = form.birth_date.data if form.birth_date.data else None
            death_date = form.death_date.data if form.death_date.data else None
            person = Person(user_id=current_user.id, name=form.name.data, birth_date=birth_date, death_date=death_date)
            db.session.add(person)
            db.session.commit()
            return redirect(url_for('persons.persons_view', username=username))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the person: {}'.format(e), 'error')
    return render_template('create_person.html', form=form, username=username)

@persons.route('/user/<username>/edit_person/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_person(username, id):
    person = Person.query.get(id)
    if person is None or person.user_id != current_user.id:
        return "Unauthorized", 403

    form = PersonForm(obj=person)
    if form.validate_on_submit():
        try:
            person.name = form.name.data
            person.birth_date = form.birth_date.data if form.birth_date.data else None
            person.death_date = form.death_date.data if form.death_date.data else None
            db.session.commit()
            flash('Person updated successfully!', 'success')
            return redirect(url_for('persons.persons_view', username=username))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the person: {}'.format(e), 'error')

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
        flash('Person deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the person: {}'.format(e), 'error')

    return redirect(url_for('persons.persons_view', username=username))
