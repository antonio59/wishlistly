from .db import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User type and relationships
    is_parent = db.Column(db.Boolean, default=False)
    is_child = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    children = db.relationship('User', backref=db.backref('parent', remote_side=[id]))
    
    # Child account settings
    date_of_birth = db.Column(db.Date, nullable=True)
    requires_parent_approval = db.Column(db.Boolean, default=True)
    can_manage_account = db.Column(db.Boolean, default=False)
    sharing_enabled = db.Column(db.Boolean, default=False)
    notifications_enabled = db.Column(db.Boolean, default=True)
    
    # Activity tracking
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Wishlists relationship
    wishlists = db.relationship('Wishlist', backref='user', lazy=True)

    @property
    def age(self):
        if self.date_of_birth:
            today = datetime.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
