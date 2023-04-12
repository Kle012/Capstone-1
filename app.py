"""Flask app for Anime."""

import requests

from flask import Flask, g, session, flash, render_template, redirect, request
from models import db, connect_db, User, Anime, Post, Favorite
from forms import RegisterForm, LoginForm, PostForm, UserEditForm
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

CURR_USER_KEY = 'curr_user'
API_BASE_URL = 'https://kitsu.io/api/edge'

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


##############################################################################
# User signup/login/logout


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


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


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
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken!", 'danger')
            return render_template('/users/signup.html', form=form)
        
        do_login(user)

        return redirect('/')
    
    else:
        return render_template('/users/signup.html', form=form)


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

    return render_template('/users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash('Bye bye!', 'success')
    return redirect ('/login')


##############################################################################
# General user routes:


@app.route('/users/<int:user_id>')
def user_detail(user_id):
    """Show user's profile."""

    user = User.query.get_or_404(user_id)
    posts = (Post.query.filter(Post.user_id == user_id).order_by(Post.created_at.desc()).limit(100).all())

    return render_template('/users/detail.html', user=user, posts=posts) 


@app.route('/users/profile', methods=['GET', 'POST'])
def edit_profile():
    """Update profile for current user."""

    if not g.user:
        flash('Access unauthorized!', 'danger')
        return redirect ('/')
    
    user = g.user
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(form.username.data, form.password.data):
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data
            user.bio = form.bio.data
            user.location = form.location.data

            db.session.commit()
            flash(f'Profile "{g.user.username}" updated.', 'success')

            return redirect (f'/users/{user.id}')
        
        flash('Wong password! Please try again', 'danger')

    return render_template('users/edit.html', form=form, user=g.user)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized!", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def show_like(user_id):
    """Show user's favorited anime list."""

    if not g.user:
        flash("Access unauthorized!", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(user_id)
    
    return render_template('users/favorites.html', user=user, favorites=user.favorites)


##############################################################################
# Posts routes:


@app.route('/posts/new', methods=['GET', 'POST'])
def posts_add():
    """Add a post:
    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash('Access unauthorized!', 'danger')
        return redirect ('/')

    form = PostForm()
    
    if form.validate_on_submit():
        post = Post(text=form.text.data)
        g.user.posts.append(post)
        db.session.commit()

        return redirect(f'/users/{g.user.id}')
    
    return render_template('posts/new.html', form=form)


@app.route('/posts/<post_id>', methods=['GET'])
def show_post(post_id):
    """Show a post."""

    post = Post.query.get(post_id)
    return render_template('posts/detail.html', post=post)


@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def posts_delete(post_id):
    """Delete a post."""

    if not g.user:
        flash("Access unauthorized!", "danger")
        return redirect("/")

    post = Post.query.get(post_id)
    if post.user_id != g.user.id:
        flash("Access unauthorized!", "danger")
        return redirect("/")

    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")


##############################################################################
# Anime routes:

@app.route('/anime')
def list_anime():
    """Page with listing of anime.
    Can take a 'q' param in querystring to search by that anime name.
    """

    search = request.args.get('q')

    if not search:
        resp = requests.get(f'{API_BASE_URL}/anime?page[limit]=20')
        list = resp.json()
    else:
        resp = requests.get(f'{API_BASE_URL}/anime?filter[text]=(%{search}%)')
        list = resp.json()
    
    return render_template ('anime/index.html', list=list)


@app.route('/anime/<int:anime_id>')
def anime_detail(anime_id):
    """Get detail of an anime."""

    resp = requests.get(f'{API_BASE_URL}/anime/{anime_id}')
    list = resp.json()

    response = requests.get(f'{API_BASE_URL}/anime/{anime_id}/streaming-links')
    link = response.json()

    return render_template('anime/detail.html', list=list, link=link)


##############################################################################
# Favorites routes:

@app.route('/anime/<int:anime_id>/favorites', methods=['POST'])
def toggle_favorite(anime_id):
    """Toggle favorite button."""

    if not g.user:
        flash('Access unauthorized!', 'danger')
        return redirect ('/')
    
    fav = Favorite.query.filter_by(user_id=g.user.id, anime_id=anime_id).first()

    resp = requests.get(f'{API_BASE_URL}/anime/{anime_id}')
    list = resp.json()

    user_fav = g.user.favorites

    if not fav:
        if not Anime.query.get(anime_id):
            anime = Anime(id=anime_id, details=list)
            db.session.add(anime)
        else:
            anime = Anime.query.get(anime_id)

        liked_anime = Favorite(user_id=g.user.id, anime_id=anime.id)
        db.session.add(liked_anime)
        user_fav.append(liked_anime)
        details = anime.details
        name = details['data']['attributes']['canonicalTitle']
        flash (f'Added { name } to Favorites.', 'success')
    
    else:
        anime = Anime.query.get(anime_id)
        details = anime.details
        name = details['data']['attributes']['canonicalTitle']
        user_fav.remove(fav)
        db.session.delete(fav)
        
        flash (f'Removed { name } from Favorites.', 'success')
    
    db.session.commit()

    return redirect ('/')


##############################################################################
# Homepage

@app.route('/')
def homepage():
    """Show homepage:
    - anon users: no messages
    - logged in: show top trending anime"""

    if g.user:
        resp = requests.get(f'{API_BASE_URL}/trending/anime')
        res = resp.json()
        return render_template('homepage.html', res=res)
    else:
        return render_template('home.html')


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404
