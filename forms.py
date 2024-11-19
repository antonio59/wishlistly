from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, URL, Optional, ValidationError
from models import User, PriorityLevel

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    is_parent = BooleanField('I am a parent')
    parent_email = StringField('Parent\'s Email', validators=[Optional(), Email()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_parent_email(self, parent_email):
        if not self.is_parent.data and not parent_email.data:
            raise ValidationError('Parent email is required for child accounts.')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')

class WishlistForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    theme = SelectField('Theme', choices=[
        ('rainbow', 'Rainbow'),
        ('space', 'Space'),
        ('unicorn', 'Unicorn'),
        ('dinosaur', 'Dinosaur')
    ])
    occasion = SelectField('Occasion', choices=[
        ('birthday', 'Birthday'),
        ('christmas', 'Christmas'),
        ('graduation', 'Graduation'),
        ('other', 'Other')
    ])
    is_public = BooleanField('Make this wishlist public')
    allow_comments = BooleanField('Allow comments')
    submit = SubmitField('Save Wishlist')

class WishlistItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    price = FloatField('Price', validators=[Optional()])
    url = StringField('URL', validators=[Optional(), URL()])
    priority = SelectField('Priority', choices=[
        (PriorityLevel.LOW.name, 'Low'),
        (PriorityLevel.MEDIUM.name, 'Medium'),
        (PriorityLevel.HIGH.name, 'High')
    ])
    quantity = StringField('Quantity', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Item')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Post Comment')
