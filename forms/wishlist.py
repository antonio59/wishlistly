from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, FloatField, SelectField, BooleanField, DateField
from wtforms.validators import DataRequired, URL, Optional, Length, NumberRange
from models.enums import PriorityLevel

class WishlistItemForm(FlaskForm):
    name = StringField('Item Name', validators=[
        DataRequired(),
        Length(min=1, max=200)
    ])
    description = TextAreaField('Description', validators=[Optional()])
    url = URLField('URL', validators=[Optional(), URL()])
    price = FloatField('Price', validators=[Optional(), NumberRange(min=0)])
    priority = SelectField('Priority', choices=PriorityLevel.choices(), default=PriorityLevel.WOULD_LIKE.value)

class WishlistForm(FlaskForm):
    name = StringField('Wishlist Name', validators=[
        DataRequired(),
        Length(min=1, max=100)
    ])
    description = TextAreaField('Description', validators=[Optional()])
    occasion = StringField('Occasion', validators=[Optional(), Length(max=100)])
    event_date = DateField('Event Date', validators=[Optional()])
    is_public = BooleanField('Public Wishlist', default=True)
    theme = SelectField('Theme', choices=[
        ('default', 'Default'),
        ('birthday', 'Birthday'),
        ('christmas', 'Christmas'),
        ('wedding', 'Wedding'),
        ('baby', 'Baby Shower'),
        ('graduation', 'Graduation')
    ], default='default')
