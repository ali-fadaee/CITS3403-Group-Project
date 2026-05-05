from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

class LoginForm(FlaskForm):
    usernameEmail = StringField(
        'Username or email address',
        validators=[DataRequired(message='Please fill in this field')]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message='Please fill in this field')]
    )
    remember = BooleanField('Remember me')
    loginSubmit = SubmitField('login --execute')

class SignupForm(FlaskForm):
    email = EmailField(
        'Email',
        validators=[
            DataRequired(message='Please fill in this field'),
            Email(message='Please enter a valid email address.')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Please fill in this field'),
            Length(min=8, message='Password must be at least 8 characters long.'),
            Regexp(r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)', message='Password does not meet requirements.')
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please fill in this field'),
            EqualTo('password', message='Passwords do not match.')
        ]
    )
    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Please fill in this field'),
            Length(min=3, max=20, message='Username does not meet requirements.'),
            Regexp(r'^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$', message='Username does not meet requirements.')
        ]
    )
    signupSubmit = SubmitField('signup --execute')