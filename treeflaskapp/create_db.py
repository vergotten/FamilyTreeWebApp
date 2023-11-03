from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Date


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////mnt/e/Python_Flask/FamilyTreeWebApp/db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(120), unique=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    date_of_birth = db.Column(Date)  # new field
    password_hash = db.Column(db.String(128))
    people = db.relationship('Person', backref='user', lazy=True)
    places = db.relationship('Place', backref='user', lazy=True)
    events = db.relationship('Event', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


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


if __name__ == '__main__':
    try:
        with app.app_context():
            # This will create all tables in the database according to the models
            # If tables already exist, it will not recreate them
            # It will also not delete any existing data in the tables
            # It's safe to call this more than once
            db.create_all()
            print("Database and tables created successfully")

    except Exception as e:
        print(f"Error creating database: {e}")
