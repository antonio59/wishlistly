from flask import Flask
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wishlist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def init_database():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()
