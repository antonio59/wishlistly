from datetime import datetime
from .db import db

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('activities', lazy=True))
    
    def __repr__(self):
        return f'<Activity {self.action} by User {self.user_id}>'
    
    @classmethod
    def log(cls, user_id, action, details=None):
        """Create a new activity log entry"""
        activity = cls(user_id=user_id, action=action, details=details)
        db.session.add(activity)
        db.session.commit()
        return activity
