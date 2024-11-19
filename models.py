from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
import jwt
import enum
from datetime import timedelta

db = SQLAlchemy()

class UserRole(str, enum.Enum):
    ADMIN = 'ADMIN'
    PARENT = 'PARENT'
    CHILD = 'CHILD'
    GUEST = 'GUEST'

class PriorityLevel(str, enum.Enum):
    NICE_TO_HAVE = 'NICE_TO_HAVE'
    WOULD_LOVE = 'WOULD_LOVE'
    MUST_HAVE = 'MUST_HAVE'

class FeedbackType(str, enum.Enum):
    BUG = 'BUG'
    FEATURE = 'FEATURE'
    GENERAL = 'GENERAL'

class User(UserMixin, db.Model):
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum(UserRole), default=UserRole.GUEST)
    is_parent = db.Column(db.Boolean, default=False)
    is_child = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    avatar_url = db.Column(db.String(200))
    
    # Relationships
    wishlists = db.relationship('Wishlist', backref='user', lazy=True)
    children = db.relationship('User', backref=db.backref('parent', remote_side=[id]))
    activities = db.relationship('Activity', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    feedback = db.relationship('Feedback', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    @property
    def is_child_account(self):
        return self.role == UserRole.CHILD and self.parent_id is not None

    def generate_email_token(self):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps(self.email, salt='email-verify')

    def verify_email_token(self, token, expiration=3600):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = s.loads(token, salt='email-verify', max_age=expiration)
            return email == self.email
        except:
            return False

    def generate_reset_token(self):
        return jwt.encode(
            {'reset_password': self.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
            return User.query.get(id)
        except:
            return None

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    theme = db.Column(db.String(50))
    occasion = db.Column(db.String(100))
    occasion_date = db.Column(db.DateTime)
    turning_age = db.Column(db.Integer)
    school_name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    share_code = db.Column(db.String(10), unique=True)
    custom_url = db.Column(db.String(50), unique=True)
    is_public = db.Column(db.Boolean, default=False)
    allow_comments = db.Column(db.Boolean, default=True)
    total_items = db.Column(db.Integer, default=0)
    total_purchased = db.Column(db.Integer, default=0)
    
    # Relationships
    items = db.relationship('WishlistItem', backref='wishlist', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='wishlist', lazy=True, cascade='all, delete-orphan')
    followers = db.relationship('WishlistFollower', backref='wishlist', lazy=True)

    def generate_share_code(self):
        if not self.share_code:
            while True:
                code = secrets.token_urlsafe(6)[:8]
                if not Wishlist.query.filter_by(share_code=code).first():
                    self.share_code = code
                    break

    def update_stats(self):
        self.total_items = len(self.items)
        self.total_purchased = len([item for item in self.items if item.purchased])
        db.session.commit()

class WishlistItem(db.Model):
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    priority = db.Column(db.Enum(PriorityLevel), default=PriorityLevel.WOULD_LOVE)
    purchased = db.Column(db.Boolean, default=False)
    purchased_by = db.Column(db.String(100))
    purchased_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlist.id'), nullable=False)
    image_url = db.Column(db.String(500))
    quantity = db.Column(db.Integer, default=1)
    notes = db.Column(db.Text)
    comments = db.relationship('Comment', backref='item', lazy=True, cascade='all, delete-orphan')

    @property
    def normalized_url(self):
        """Normalize URL to include https:// if not present"""
        if not self.url:
            return None
        if self.url.startswith('www.'):
            return f'https://{self.url}'
        if not self.url.startswith(('http://', 'https://')):
            return f'https://www.{self.url}'
        return self.url

class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('wishlist_item.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlist.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('wishlist_item.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    
    # Relationships
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    emoji = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    related_wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlist.id'))
    related_item_id = db.Column(db.Integer, db.ForeignKey('wishlist_item.id'))
    is_public = db.Column(db.Boolean, default=True)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    action_url = db.Column(db.String(200))

class WishlistFollower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlist.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'wishlist_id', name='unique_follower'),)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(FeedbackType), nullable=False, default=FeedbackType.GENERAL)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(50), default='NEW')  # NEW, IN_PROGRESS, RESOLVED, CLOSED
    priority = db.Column(db.String(50), default='MEDIUM')  # LOW, MEDIUM, HIGH
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    browser_info = db.Column(db.String(500))
    url = db.Column(db.String(500))
    
    # Relationship with User
    user = db.relationship('User', backref=db.backref('feedback', lazy=True))

    def __repr__(self):
        return f'<Feedback {self.id}: {self.type} - {self.title}>'
