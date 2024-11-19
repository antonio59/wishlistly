from flask import Blueprint
from .main import main
from .feedback import feedback_bp

def init_app(app):
    app.register_blueprint(main)
    app.register_blueprint(feedback_bp)
