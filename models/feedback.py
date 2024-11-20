from datetime import datetime
from .db import db
from .enums import FeedbackType

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120))
    url = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='new')  # new, in_progress, resolved, closed
    admin_notes = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('feedback', lazy=True))
    
    def __repr__(self):
        return f'<Feedback {self.type}: {self.title}>'
    
    @property
    def feedback_type(self):
        """Get the feedback type as an enum"""
        return FeedbackType(self.type)
    
    @feedback_type.setter
    def feedback_type(self, value):
        """Set the feedback type from an enum"""
        if isinstance(value, FeedbackType):
            self.type = value.value
        else:
            self.type = str(value)
