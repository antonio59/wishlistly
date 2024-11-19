from flask import Blueprint, render_template
from flask_login import current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/parent-guide')
def parent_guide():
    return render_template('guides/parent_guide.html')

@main.route('/kid-guide')
def child_guide():
    return render_template('guides/child_guide.html')

@main.route('/faq')
def faq():
    return render_template('faq.html')

@main.route('/help')
def help():
    return render_template('help.html')

@main.route('/privacy')
def privacy_policy():
    return render_template('legal/privacy_policy.html')

@main.route('/terms')
def terms():
    return render_template('legal/terms.html')

@main.route('/cookie-policy')
def cookie_policy():
    return render_template('legal/cookie_policy.html')

@main.route('/support')
def support():
    """Support page with Ko-Fi integration."""
    return render_template('support.html')
