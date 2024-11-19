from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from datetime import datetime
from models import db, User, Activity, Notification, UserRole
from forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from email_utils import send_password_reset_email, send_verification_email

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'error')
            return redirect(url_for('auth.login'))
            
        if not user.email_verified:
            flash('Please verify your email address first.', 'warning')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Record login activity
        activity = Activity(
            user_id=user.id,
            activity_type='login',
            message=f'Logged in from {request.remote_addr}',
            emoji='🔐'
        )
        db.session.add(activity)
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@auth.route('/logout')
@login_required
def logout():
    activity = Activity(
        user_id=current_user.id,
        activity_type='logout',
        message='Logged out',
        emoji='👋'
    )
    db.session.add(activity)
    db.session.commit()
    
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            role=UserRole.PARENT if form.is_parent.data else UserRole.CHILD
        )
        user.set_password(form.password.data)
        
        if form.parent_email.data and not form.is_parent.data:
            parent = User.query.filter_by(email=form.parent_email.data.lower()).first()
            if parent and parent.is_parent:
                user.parent_id = parent.id
            else:
                flash('Parent email not found or is not a parent account', 'error')
                return redirect(url_for('auth.register'))
        
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        token = user.generate_email_token()
        send_verification_email(user.email, token)
        
        # Create welcome notification
        notification = Notification(
            user_id=user.id,
            title='Welcome to Kids Wishlist!',
            message='Thank you for joining. Start by creating your first wishlist!',
            type='welcome'
        )
        db.session.add(notification)
        
        # Record registration activity
        activity = Activity(
            user_id=user.id,
            activity_type='registration',
            message='Registered new account',
            emoji='👋'
        )
        db.session.add(activity)
        db.session.commit()
        
        flash('Registration successful! Please check your email to verify your account.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/verify/<token>')
def verify_email(token):
    user = User.query.filter_by(email=token).first()
    if user is None:
        flash('Invalid verification link', 'error')
        return redirect(url_for('main.index'))
    
    if user.email_verified:
        flash('Email already verified', 'info')
        return redirect(url_for('auth.login'))
    
    if user.verify_email_token(token):
        user.email_verified = True
        db.session.commit()
        flash('Your email has been verified! You can now log in.', 'success')
    else:
        flash('The verification link is invalid or has expired', 'error')
    
    return redirect(url_for('auth.login'))

@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_password_reset_email(user.email, token)
            flash('Check your email for instructions to reset your password', 'info')
        else:
            flash('Email address not found', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired reset link', 'error')
        return redirect(url_for('main.index'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        
        # Record password reset activity
        activity = Activity(
            user_id=user.id,
            activity_type='password_reset',
            message='Reset password',
            emoji='🔑',
            is_public=False
        )
        db.session.add(activity)
        
        # Create notification
        notification = Notification(
            user_id=user.id,
            title='Password Reset Successful',
            message='Your password has been reset successfully.',
            type='security'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Your password has been reset', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='Reset Password', form=form)

@auth.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('auth/settings.html', title='Account Settings')
