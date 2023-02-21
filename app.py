"""Flask app for Anime."""

import requests

from flask import Flask, g, session, flash, render_template, redirect
from models import db, connect_db, User
from forms import RegisterForm, LoginForm
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

CURR_USER_KEY = 'curr_user'
API_BASE_URL = "https://kitsu.io/api/edge"

app = Flask(__name__)
app.config['SECRET_KEY'] = ('oh-secret-thing')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///anime'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)
with app.app_context():
    db.drop_all()
    db.create_all()

@app.before_request
def add_user_to_g():
    """If we're logged out, add curr user to Flask global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id

def do_logout(user):
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/')
def homepage():
    res = requests.get(f'{API_BASE_URL}/trending/anime')
    # data = res.json()
    # title = data['titles'][0]['en']
    # return render_template('homepage.html', anime=anime)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If there already is a user with that username, flash message and re-present form.
    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User.signup(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                username=form.username.data,
                password=form.password.data,
                email=form.email.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)
        
        do_login(user)

        return redirect('/')
    
    else:
        return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash (f'Hello, {user.username}!', 'success')
            return redirect('/')

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash('Bye bye!', 'success')
    return redirect ('/login')



##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
