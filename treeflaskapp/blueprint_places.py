# places.py
from flask import Blueprint, request, render_template, redirect, url_for, g, flash
from flask_login import login_required, current_user
from .models import Place, db
from .forms import PlaceForm

places = Blueprint('places', __name__)

@places.route('/user/<username>/places')
def places_view(username):
    if username == current_user.username:
        places = Place.query.filter_by(user_id=current_user.id).all()
        form = PlaceForm(user_language=g.user_language)  # create an instance of your form
        return render_template('places.html', places=places, form=form)
    else:
        return "Unauthorized", 403

@places.route('/user/<username>/create_place', methods=['GET', 'POST'])
@login_required
def create_place(username):
    form = PlaceForm(user_language=g.user_language)
    if form.validate_on_submit():
        try:
            place = Place(user_id=current_user.id, name=form.name.data, location=form.location.data, significance=form.significance.data)
            db.session.add(place)
            db.session.commit()
            flash_message = 'Place created successfully!' if g.user_language == 'en' else 'Место успешно создано!'
            flash(flash_message, 'success')
            return redirect(url_for('places.places_view', username=username))
        except Exception as e:
            db.session.rollback()
            flash_message = 'An error occurred while creating the place: {}'.format(e) if g.user_language == 'en' \
                else 'Произошла ошибка при создании места: {}'.format(e)
            flash(flash_message, 'error')
    return render_template('create_place.html', form=form, username=username)

@places.route('/user/<username>/edit_place/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_place(username, id):
    place = Place.query.get(id)
    if place is None or place.user_id != current_user.id:
        return "Unauthorized", 403

    form = PlaceForm(obj=place, user_language=g.user_language)
    if form.validate_on_submit():
        try:
            place.name = form.name.data
            place.location = form.location.data
            place.significance = form.significance.data
            db.session.commit()
            flash_message = 'Place updated successfully!' if g.user_language == 'en' else 'Место успешно обновлено!'
            flash(flash_message, 'success')
            return redirect(url_for('persons.persons_view', username=username))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the place: {}'.format(e), 'error')

    return render_template('edit_place.html', form=form, username=username, place=place)

@places.route('/user/<username>/delete_place/<int:id>', methods=['POST'])
@login_required
def delete_place(username, id):
    place = Place.query.get(id)
    if place is None or place.user_id != current_user.id:
        return "Unauthorized", 403

    try:
        db.session.delete(place)
        db.session.commit()
        flash_message = 'Place deleted successfully!' if g.user_language == 'en' else 'Место успешно удалено!'
        flash(flash_message, 'success')
    except Exception as e:
        db.session.rollback()
        flash_message = 'An error occurred while deleting the place: {}'.format(e) if g.user_language == 'en' \
            else 'Произошла ошибка при удалении места: {}'.format(e)
        flash(flash_message, 'error')

    return redirect(url_for('places.places_view', username=username))
