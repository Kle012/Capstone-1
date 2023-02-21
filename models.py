"""Models for Anime app."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)

class User(db.Model):
    """User in the system."""
    __tablename__ = 'users'

    id = db.Column (db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column (db.Text, nullable=False)
    last_name = db.Column (db.Text, nullable=False)
    username = db.Column (db.Text, nullable=False, unique=True)
    password = db.Column (db.Text, nullable=False)
    email = db.Column (db.Text, nullable=False, unique=True)

    def __repr__(self):
        return f'<User #{self.id}: {self.username}, {self.email}>'
    
    @classmethod
    def signup(cls, first_name, last_name, username, email, password):
        """Sign up user.
        Hashes password and adds user to the system.
        """
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=hashed_pwd
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        It searches for a user whose password hash matches this password, and if it finds such a user, returns that user object.
        If it can't find matching user (or if password is wrong), returns False."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
            
        return False
    
    posts = db.relationship('Post')
    
    favorites = db.relationship('User', secondary='animes')

class Anime(db.Model):
    """Anime in the system."""
    __tablename__ = 'animes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text)

class Post(db.Model):
    """An individual post."""
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey('animes.id', ondelete='CASCADE'), nullable=False)

    user = db.relationship('User')

class Favorite(db.Model):
    """Connection of a user <-> anime."""
    __tablename__ = 'favorites'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    anime_id = db.Column(db.Integer, db.ForeignKey('animes.id', ondelete='CASCADE'), primary_key=True)
    