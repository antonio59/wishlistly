from flask import Flask
from models import db
from migrations.update_priority_levels import upgrade

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wishlist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def run_migration():
    with app.app_context():
        print("Starting priority level migration...")
        upgrade()
        print("Migration completed successfully!")

if __name__ == '__main__':
    run_migration()
