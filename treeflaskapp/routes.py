from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from treeflaskapp import app, db, login_manager
from treeflaskapp.models import User
from treeflaskapp.forms import LoginForm, RegisterForm
from flask import flash, session, g


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
    return render_template(g.user_language + '/index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data, date_of_birth=form.date_of_birth.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template(g.user_language + '/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            session['username'] = user.username  # store the username in session
            return redirect(url_for('user_profile', username=user.username))  # redirect to user's profile
        else:
            flash('Incorrect username or password. Please try again.')
    return render_template(g.user_language + '/login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    session.pop('username', None)  # clear the username from session
    return redirect(url_for('index'))  # redirect to the index page

@app.route('/user/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template(g.user_language + '/user_panel.html', user=user)

@app.route('/user/<username>/persons')
def persons(username):
    # Your code here
    return render_template(g.user_language + '/persons.html')

@app.route('/user/<username>/places')
def places(username):
    # Your code here
    return render_template(g.user_language + '/places.html')
