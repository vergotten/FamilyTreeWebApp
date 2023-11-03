from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import flash, redirect, url_for
from sqlalchemy import Date

from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(120), unique=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    date_of_birth = db.Column(Date)
    password_hash = db.Column(db.String(128))
    people = db.relationship('Person', backref='user', lazy=True)
    places = db.relationship('Place', backref='user', lazy=True)
    events = db.relationship('Event', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        flash('You do not have access to this page. Please log in first.')
        return redirect(url_for('login'))

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    death_date = db.Column(db.Date)
    image_file = db.Column(db.String(120), nullable=True)

class Relationship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person1_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    person2_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    relationship_type = db.Column(db.String(50))

class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100))
    location = db.Column(db.String(200))
    significance = db.Column(db.Text)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100))
    date = db.Column(db.Date)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))
