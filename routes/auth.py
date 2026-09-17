from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models.db import db
from datetime import datetime
import re

auth = Blueprint('auth', __name__)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        is_parent = request.form.get('account_type') == 'parent'

        if not all([email, username, password, confirm_password]):
            flash('All fields are required', 'error')
            return redirect(url_for('auth.register'))

        if not is_valid_email(email):
            flash('Please enter a valid email address', 'error')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return redirect(url_for('auth.register'))

        user = User(
            email=email,
            username=username,
            password=generate_password_hash(password),
            is_parent=is_parent,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('auth/register.html')

@auth.route('/register-child', methods=['GET', 'POST'])
@login_required
def register_child():
    if not current_user.is_parent:
        flash('Only parent accounts can register children', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        date_of_birth = request.form.get('date_of_birth')

        if not all([username, password, confirm_password, date_of_birth]):
            flash('All fields are required', 'error')
            return redirect(url_for('auth.register_child'))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register_child'))

        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return redirect(url_for('auth.register_child'))

        try:
            dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'error')
            return redirect(url_for('auth.register_child'))

        child = User(
            username=username,
            email=f"{username}@child.wishlistly.net",  # Internal email for child accounts
            password=generate_password_hash(password),
            is_parent=False,
            parent_id=current_user.id,
            date_of_birth=dob,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )

        # Set age-based permissions
        age = child.age
        if age is not None and age < 13:
            child.requires_parent_approval = True
            child.can_manage_account = False
        else:
            child.requires_parent_approval = False
            child.can_manage_account = True

        db.session.add(child)
        db.session.commit()

        flash('Child account created successfully!', 'success')
        return redirect(url_for('parent.dashboard'))

    return render_template('auth/register_child.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not all([email, password]):
            flash('All fields are required', 'error')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            user.last_activity = datetime.utcnow()
            db.session.commit()
            
            if user.is_parent:
                return redirect(url_for('parent.dashboard'))
            return redirect(url_for('main.dashboard'))

        flash('Invalid email or password', 'error')
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('main.index'))

@auth.route('/switch-account/<int:user_id>')
@login_required
def switch_account(user_id):
    if not current_user.is_parent:
        target_user = User.query.get_or_404(user_id)
        if target_user.id != current_user.parent_id:
            flash('Unauthorized access', 'error')
            return redirect(url_for('main.dashboard'))
    else:
        target_user = User.query.filter_by(id=user_id, parent_id=current_user.id).first_or_404()

    login_user(target_user)
    flash(f'Switched to {target_user.username}\'s account', 'success')
    
    if target_user.is_parent:
        return redirect(url_for('parent.dashboard'))
    return redirect(url_for('main.dashboard'))
