from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms.auth import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from models.user import User
from models.db import db
from utils.security import rate_limit, generate_reset_token, verify_reset_token, update_password_hash
from utils.email import send_password_reset_email
from oauthlib.oauth2 import WebApplicationClient
import requests
import json
from datetime import datetime, timedelta
import secrets

auth = Blueprint('auth', __name__)

def get_google_client():
    """Get the Google OAuth client with current application context"""
    return WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])

@auth.route('/login', methods=['GET', 'POST'])
@rate_limit(limit=5, window=300)  # 5 attempts per 5 minutes
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            return redirect(next_page)
        flash('Invalid email or password', 'danger')
    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
@rate_limit(limit=3, window=3600)  # 3 registrations per hour
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.lower(),
            username=form.username.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = generate_reset_token(user)
            send_password_reset_email(user, token)
            flash('Check your email for instructions to reset your password', 'info')
            return redirect(url_for('auth.login'))
        flash('If an account exists with that email, you will receive reset instructions.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = verify_reset_token(token)
    if not user:
        flash('Invalid or expired reset token', 'danger')
        return redirect(url_for('auth.reset_password_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        update_password_hash(user, form.password.data)
        flash('Your password has been reset', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

def get_google_provider_cfg():
    return requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()

@auth.route('/login/google')
def google_login():
    google_client = get_google_client()
    
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg['authorization_endpoint']
    
    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = google_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + '/callback',
        scope=['openid', 'email', 'profile'],
    )
    return redirect(request_uri)

@auth.route('/login/google/callback')
def google_callback():
    google_client = get_google_client()
    
    # Get authorization code Google sent back
    code = request.args.get('code')
    if not code:
        flash('Google authentication failed', 'danger')
        return redirect(url_for('auth.login'))
    
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg['token_endpoint']
    
    # Prepare and send request to get tokens
    token_url, headers, body = google_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
    )
    
    # Parse the tokens
    google_client.parse_request_body_response(json.dumps(token_response.json()))
    
    # Get user info from Google
    userinfo_endpoint = google_provider_cfg['userinfo_endpoint']
    uri, headers, body = google_client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    
    if userinfo_response.json().get('email_verified'):
        google_id = userinfo_response.json()['sub']
        email = userinfo_response.json()['email']
        name = userinfo_response.json().get('given_name', email.split('@')[0])
        
        # Check if user exists
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            # Check if email is already registered
            user = User.query.filter_by(email=email).first()
            if user:
                # Link Google ID to existing account
                user.google_id = google_id
                db.session.commit()
            else:
                # Create new user
                user = User(
                    email=email,
                    username=name,
                    google_id=google_id,
                    password_hash=generate_password_hash(secrets.token_urlsafe(32))
                )
                db.session.add(user)
                db.session.commit()
        
        login_user(user)
        user.update_last_login()
        flash('Successfully logged in with Google', 'success')
        return redirect(url_for('main.index'))
    else:
        flash('Google authentication failed: Email not verified', 'danger')
        return redirect(url_for('auth.login'))
