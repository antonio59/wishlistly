from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import current_user, login_required
from models.user import User
from models.wishlist import Wishlist
from models.activity import Activity
from models.db import db
from models.feedback import FeedbackType
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_parent:
            return redirect(url_for('parent_dashboard'))
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/support')
def support():
    return render_template('support.html')

@main.route('/kids-safety')
def kids_safety():
    return render_template('kids_safety.html')

@main.route('/feedback', methods=['GET', 'POST'])
def feedback():
    feedback_type = request.args.get('type', 'GENERAL')
    if request.method == 'POST':
        feedback_text = request.form.get('feedback')
        if feedback_text:
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('main.index'))
    return render_template('feedback_form.html', feedback_type=feedback_type, feedback_types=FeedbackType)

@main.route('/faq')
def faq():
    return render_template('faq.html')

@main.route('/help')
def help():
    return render_template('help.html')

# Legal routes
@main.route('/privacy')
def privacy_policy():
    return render_template('legal/privacy_policy.html')

@main.route('/terms')
def terms():
    return render_template('legal/terms.html')

@main.route('/cookies')
def cookie_policy():
    return render_template('legal/cookie_policy.html')

# Guide routes
@main.route('/parent-guide')
def parent_guide():
    return render_template('guides/parent_guide.html')

@main.route('/child-guide')
def child_guide():
    return render_template('guides/child_guide.html')
