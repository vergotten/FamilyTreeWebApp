from flask import Flask, flash, redirect, url_for, request, g, session
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

def get_user_language():
    # Get the 'Accept-Language' header from the request
    languages = request.accept_languages

    # The header contains a list of languages the client can understand,
    # as well as a quality value for each language. The quality value
    # represents the user's preference for that language (1 is highest).
    # We'll assume that the first language in the list is the user's
    # preferred language.
    preferred_language = languages[0][0]

    # Now we'll map the preferred language to one of our supported languages.
    # If we don't support the preferred language, we'll default to English.
    if preferred_language.startswith('ru'):
        return 'ru'
    else:
        return 'en'

@app.before_request
def before_request():
    g.user_language = session.get('user_language')
    if g.user_language not in ['en', 'ru']:
        g.user_language = 'en'  # default to English if no valid language is set in session


# Import routes and models after db has been defined
from treeflaskapp.models import *

# Import routes and models after db has been defined
from treeflaskapp import routes
