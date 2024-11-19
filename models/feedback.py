from . import db
from datetime import datetime

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # 'bug' or 'feature'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120))
    url = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='new')  # new, in_progress, resolved, closed
    admin_notes = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('feedback', lazy=True))
    
    def __repr__(self):
        return f'<Feedback {self.type}: {self.title}>'
