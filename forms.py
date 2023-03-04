from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Optional

class RegisterForm (FlaskForm):
    """Form for adding user."""
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    email = StringField('E-mail', validators=[InputRequired(), Email()])
    image_url = StringField('(Optional) Image URL', validators=[Optional()])


class UserEditForm (FlaskForm):
    """Form to edit a user's profile."""
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    email = StringField('E-mail', validators=[InputRequired(), Email()])
    location = StringField('Location', validators=[Optional()])
    bio = TextAreaField('Bio', validators=[Optional()])
    image_url = StringField('(Optional) Image URL', validators=[Optional()])


class LoginForm (FlaskForm):
    """Form for user to log in."""
    username = StringField('Username', validators = [InputRequired()])
    password = PasswordField('Password', validators = [InputRequired()])


class PostForm (FlaskForm):
    """Form to add a post."""
    text = TextAreaField('Post', validators=[InputRequired()])