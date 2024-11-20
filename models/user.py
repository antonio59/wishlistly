from flask_login import UserMixin
from .db import db
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Role fields
    is_parent = db.Column(db.Boolean, default=False)
    is_child = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Password reset fields
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expiry = db.Column(db.DateTime)
    
    # OAuth fields
    google_id = db.Column(db.String(100), unique=True)
    
    # Relationships
    wishlists = db.relationship('Wishlist', backref='owner', lazy=True)
    children = db.relationship('User', backref=db.backref('parent', remote_side=[id]),
                             lazy=True, foreign_keys=[parent_id])
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def set_password_reset_token(self, token, expiry):
        self.reset_token = token
        self.reset_token_expiry = expiry
        db.session.commit()
    
    def clear_password_reset_token(self):
        self.reset_token = None
        self.reset_token_expiry = None
        db.session.commit()
        
    @property
    def role(self):
        if self.is_parent:
            return 'parent'
        elif self.is_child:
            return 'child'
        return 'user'
    
    def get_children(self):
        """Get all children accounts linked to this parent"""
        if not self.is_parent:
            return []
        return self.children
    
    def get_parent(self):
        """Get the parent account if this is a child account"""
        if not self.is_child:
            return None
        return self.parent
