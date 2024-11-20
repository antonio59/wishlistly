from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models.user import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=25)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long'),
        # Custom password complexity validator could be added here
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    accept_tos = BooleanField('I accept the Terms of Service', validators=[
        DataRequired(message='You must accept the Terms of Service')
    ])
    submit = SubmitField('Create Account')

    def validate_email(self, field):
        """Check if email is already registered"""
        user = User.query.filter_by(email=field.data.lower()).first()
        if user:
            raise ValidationError('This email is already registered. Please use a different email or log in.')

    def validate_username(self, field):
        """Check if username is already taken"""
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('This username is already taken. Please choose a different one.')

    def validate_password(self, field):
        """Custom password validation"""
        password = field.data
        
        # Check for at least one number
        if not any(char.isdigit() for char in password):
            raise ValidationError('Password must contain at least one number')
        
        # Check for at least one uppercase letter
        if not any(char.isupper() for char in password):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        # Check for at least one lowercase letter
        if not any(char.islower() for char in password):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        # Check for at least one special character
        special_chars = "!@#$%^&*(),.?\":{}|<>"
        if not any(char in special_chars for char in password):
            raise ValidationError('Password must contain at least one special character')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
