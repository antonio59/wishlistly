from .db import db
from datetime import datetime

class SharingRequest(db.Model):
    __tablename__ = 'sharing_requests'

    id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlists.id'), nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    wishlist = db.relationship('Wishlist', backref='sharing_requests')
    child = db.relationship('User', foreign_keys=[child_id], backref='sharing_requests_made')
    parent = db.relationship('User', foreign_keys=[parent_id], backref='sharing_requests_received')

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # sharing_request, wishlist_update, etc.
    message = db.Column(db.String(255), nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optional reference IDs
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlists.id'), nullable=True)
    sharing_request_id = db.Column(db.Integer, db.ForeignKey('sharing_requests.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    wishlist = db.relationship('Wishlist', backref='notifications')
    sharing_request = db.relationship('SharingRequest', backref='notifications')
