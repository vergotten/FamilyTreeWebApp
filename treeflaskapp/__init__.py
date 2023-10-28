from flask import Flask, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from config import Config
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from treeflaskapp.models import User  # Import User inside the function to avoid circular imports
    return User.query.get(int(user_id))

# Import routes and models after db has been defined
from treeflaskapp.models import User, UserAdmin  # Import your models here

# Import routes and models after db has been defined
from treeflaskapp import routes

