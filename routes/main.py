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
            return redirect(url_for('main.parent_dashboard'))
        return redirect(url_for('main.dashboard'))
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

# Dashboard routes
@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_parent:
        return redirect(url_for('main.parent_dashboard'))
    
    wishlists = Wishlist.query.filter_by(user_id=current_user.id).all()
    activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.created_at.desc()).limit(10).all()
    
    return render_template('dashboard.html', wishlists=wishlists, activities=activities)

@main.route('/parent-dashboard')
@login_required
def parent_dashboard():
    if not current_user.is_parent:
        return redirect(url_for('main.dashboard'))
    
    children = User.query.filter_by(parent_id=current_user.id).all()
    child_activities = []
    for child in children:
        activities = Activity.query.filter_by(user_id=child.id).order_by(Activity.created_at.desc()).limit(5).all()
        child_activities.extend(activities)
    
    child_activities.sort(key=lambda x: x.created_at, reverse=True)
    child_activities = child_activities[:10]
    
    return render_template('parent_dashboard.html', children=children, activities=child_activities)

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
