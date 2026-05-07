from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
from app.models import User

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
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('An account already exists with this email.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already taken.')