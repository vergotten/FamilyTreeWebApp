# events.py
from flask import Blueprint, request, render_template, redirect, url_for, g, flash
from flask_login import login_required, current_user
from .models import Event, db
from .forms import EventForm

events = Blueprint('events', __name__)

@events.route('/user/<username>/events')
def events_view(username):
    if username == current_user.username:
        events = Event.query.filter_by(user_id=current_user.id).all()
        form = EventForm(user_language=g.user_language)  # create an instance of your form
        return render_template('events.html', events=events, form=form)
    else:
        return "Unauthorized", 403

@events.route('/user/<username>/create_event', methods=['GET', 'POST'])
@login_required
def create_event(username):
    form = EventForm(user_language=g.user_language)
    if form.validate_on_submit():
        try:
            event = Event(user_id=current_user.id, name=form.name.data, date=form.date.data)
            db.session.add(event)
            db.session.commit()
            flash_message = 'Event created successfully!' if g.user_language == 'en' else 'Событие успешно создано!'
            flash(flash_message, 'success')
            return redirect(url_for('events.events_view', username=username))
        except Exception as e:
            db.session.rollback()
            flash_message = 'An error occurred while creating the event: {}'.format(e) if g.user_language == 'en' \
                else 'Произошла ошибка при создании события: {}'.format(e)
            flash(flash_message, 'error')
    return render_template('create_event.html', form=form, username=username)

@events.route('/user/<username>/edit_event/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(username, id):
    event = Event.query.get(id)
    if event is None or event.user_id != current_user.id:
        return "Unauthorized", 403

    form = EventForm(obj=event, user_language=g.user_language)
    if form.validate_on_submit():
        try:
            event.name = form.name.data
            event.date = form.date.data
            db.session.commit()
            flash_message = 'Event updated successfully!' if g.user_language == 'en' else 'Событие успешно обновлено!'
            flash(flash_message, 'success')
            return redirect(url_for('events.events_view', username=username))
        except Exception as e:
            db.session.rollback()
            flash_message = 'An error occurred while updating the event: {}'.format(e) if g.user_language == 'en' \
                else 'Произошла ошибка при обновлении события: {}'.format(e)
            flash(flash_message, 'error')

    return render_template('edit_event.html', form=form, username=username, event=event)

@events.route('/user/<username>/delete_event/<int:id>', methods=['POST'])
@login_required
def delete_event(username, id):
    event = Event.query.get(id)
    if event is None or event.user_id != current_user.id:
        return "Unauthorized", 403

    try:
        db.session.delete(event)
        db.session.commit()
        flash_message = 'Event deleted successfully!' if g.user_language == 'en' else 'Событие успешно удалено!'
        flash(flash_message, 'success')
    except Exception as e:
        db.session.rollback()
        flash_message = 'An error occurred while deleting the event: {}'.format(e) if g.user_language == 'en' \
            else 'Произошла ошибка при удалении события: {}'.format(e)
        flash(flash_message, 'error')

    return redirect(url_for('events.events_view', username=username))
