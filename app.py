from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import secrets
import logging
from dotenv import load_dotenv
import random
import string
import re
from themes import OCCASIONS, WISHLIST_THEMES, get_themes_by_occasion, get_theme_by_id
from demo import get_demo_wishlists, DemoWishlist
from models import db
from routes import init_app as init_routes

load_dotenv()

app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/antoniosmith/CascadeProjects/kidswishlist/instance/kidswishlist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Enable SQL logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configure upload settings
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_IMAGES_PER_ITEM = 2

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db.init_app(app)
init_routes(app)
migrate = Migrate(app, db)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def utility_processor():
    return {'now': datetime.now()}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_images(files):
    saved_files = []
    if not files:
        return saved_files
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to filename to make it unique
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_files.append(filename)
            
            if len(saved_files) >= MAX_IMAGES_PER_ITEM:
                break
                
    return saved_files

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_parent:
            return redirect(url_for('parent_dashboard'))
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_parent:
            return redirect(url_for('parent_dashboard'))
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            
            # Create welcome activity if this is their first login
            if not Activity.query.filter_by(user_id=user.id).first():
                activity = Activity(
                    user_id=user.id,
                    activity_type="LOGIN",
                    message=f"Welcome to Kids Wishlist! Account created as {'parent' if user.is_parent else 'child'}.",
                    emoji="👋"
                )
                db.session.add(activity)
                db.session.commit()
            
            # Redirect based on account type
            if user.is_parent:
                return redirect(url_for('parent_dashboard'))
            return redirect(url_for('dashboard'))
            
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # If user is a parent and not viewing as child, redirect to parent dashboard
    if current_user.is_parent and 'parent_id' not in session:
        return redirect(url_for('parent_dashboard'))
    
    # Get user's wishlists
    wishlists = Wishlist.query.filter_by(user_id=current_user.id).all()
    
    # Get recent activities
    activities = Activity.query.filter_by(user_id=current_user.id)\
        .order_by(Activity.timestamp.desc())\
        .limit(5)\
        .all()
    
    return render_template('dashboard.html', 
                         wishlists=wishlists,
                         activities=activities)

@app.route('/parent_dashboard')
@login_required
def parent_dashboard():
    # Check if user is a parent
    if not current_user.is_parent:
        flash('Access denied. This page is only for parent accounts.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if parent is viewing as child
    if 'parent_id' in session:
        flash('Please switch back to your parent account first.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Get all children associated with this parent
    children = User.query.filter_by(parent_id=current_user.id).all()
    
    # Prepare data for each child
    children_data = []
    for child in children:
        wishlists = Wishlist.query.filter_by(user_id=child.id).all()
        total_items = sum(len(wishlist.items.all()) for wishlist in wishlists)
        activities = Activity.query.filter_by(user_id=child.id)\
            .order_by(Activity.timestamp.desc())\
            .limit(5)\
            .all()
        
        children_data.append({
            'child': child,
            'wishlists': wishlists,
            'total_items': total_items,
            'activities': activities
        })
    
    # Get all activities across children for the activity feed
    all_activities = []
    for child in children:
        child_activities = Activity.query.filter_by(user_id=child.id)\
            .order_by(Activity.timestamp.desc())\
            .limit(5)\
            .all()
        all_activities.extend(child_activities)
    
    # Sort activities by timestamp
    all_activities.sort(key=lambda x: x.timestamp, reverse=True)
    
    return render_template('parent_dashboard.html', 
                         children_data=children_data,
                         activities=all_activities[:10])

@app.route('/switch_to_child/<int:child_id>')
@login_required
def switch_to_child(child_id):
    if not current_user.is_parent:
        flash('Access denied. Only parent accounts can switch to child views.', 'danger')
        return redirect(url_for('dashboard'))
    
    child = User.query.get_or_404(child_id)
    if child.parent_id != current_user.id:
        flash('Access denied. You can only view your own children\'s accounts.', 'danger')
        return redirect(url_for('parent_dashboard'))
    
    session['parent_id'] = current_user.id
    logout_user()
    login_user(child)
    
    flash(f'Switched to {child.username}\'s account', 'success')
    return redirect(url_for('dashboard'))

@app.route('/switch_to_parent')
@login_required
def switch_to_parent():
    if 'parent_id' in session:
        parent = User.query.get(session['parent_id'])
        if parent and parent.is_parent:
            logout_user()
            login_user(parent)
            session.pop('parent_id', None)
            flash('Switched back to parent account.', 'success')
            return redirect(url_for('parent_dashboard'))
    
    flash('Unable to switch to parent account.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/view_child_details/<int:child_id>')
@login_required
def view_child_details(child_id):
    if not current_user.is_parent:
        flash('Access denied. Parent account required.', 'error')
        return redirect(url_for('dashboard'))
    
    child = User.query.filter_by(id=child_id, parent_id=current_user.id).first_or_404()
    return render_template('child_details.html', child=child)

@app.route('/api/activities/latest')
@login_required
def get_latest_activities():
    if not current_user.is_parent:
        return jsonify({'error': 'Access denied'}), 403
    
    children_ids = [child.id for child in User.query.filter_by(parent_id=current_user.id).all()]
    activities = []
    
    for child_id in children_ids:
        child_activities = Activity.query.filter_by(user_id=child_id)\
            .order_by(Activity.timestamp.desc())\
            .limit(5)\
            .all()
        
        activities.extend([{
            'child_id': activity.user_id,
            'message': activity.message,
            'emoji': activity.emoji,
            'timestamp': activity.timestamp.isoformat()
        } for activity in child_activities])
    
    return jsonify(activities)

@app.route('/create_wishlist', methods=['GET', 'POST'])
@login_required
def create_wishlist():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        theme = request.form.get('theme', 'default')
        occasion = request.form.get('occasion')
        
        if not title:
            flash('Title is required!', 'error')
            return redirect(url_for('create_wishlist'))
        
        # Create new wishlist
        wishlist = Wishlist(
            title=title,
            description=description,
            theme=theme,
            occasion=occasion,
            user_id=current_user.id
        )
        
        # Add occasion-specific details if provided
        if occasion == 'birthday' and request.form.get('birthday_date'):
            try:
                wishlist.occasion_date = datetime.strptime(request.form.get('birthday_date'), '%Y-%m-%d')
                if request.form.get('turning_age'):
                    wishlist.turning_age = int(request.form.get('turning_age'))
            except (ValueError, TypeError) as e:
                app.logger.error(f"Error parsing birthday details: {str(e)}")
                
        elif occasion == 'graduation' and request.form.get('graduation_date'):
            try:
                wishlist.occasion_date = datetime.strptime(request.form.get('graduation_date'), '%Y-%m-%d')
                wishlist.school_name = request.form.get('school_name')
            except ValueError as e:
                app.logger.error(f"Error parsing graduation date: {str(e)}")
        
        # Generate share code
        wishlist.generate_share_code()
        
        db.session.add(wishlist)
        db.session.flush()  # This will assign an ID to wishlist before we create the activity
        
        # Create activity record
        activity = Activity(
            user_id=current_user.id,
            message=f"Created new wishlist: {title}",
            emoji="🎁",
            related_wishlist_id=wishlist.id,
            activity_type="CREATE_WISHLIST",
            is_public=True,
            timestamp=datetime.utcnow()
        )
        db.session.add(activity)
        
        try:
            db.session.commit()
            flash('Wishlist created successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating wishlist: {str(e)}")
            app.logger.error(f"Full error: {repr(e)}")
            flash(f'An error occurred while creating the wishlist: {str(e)}', 'error')
            return redirect(url_for('create_wishlist'))
    
    # GET request - render the create wishlist form with all themes and occasions
    return render_template('create_wishlist.html', 
                         themes=WISHLIST_THEMES,
                         occasions=OCCASIONS)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            app.logger.info("Starting user registration process...")
            
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            account_type = request.form.get('account_type')
            
            app.logger.info(f"Received registration for username: {username}, email: {email}, account_type: {account_type}")
            
            # Input validation
            if not all([username, email, password, account_type]):
                app.logger.error("Missing required registration fields")
                flash('All fields are required.', 'danger')
                return render_template('register.html')
            
            # Check if username exists using a fresh query
            existing_user = db.session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                if existing_user.username == username:
                    app.logger.warning(f"Username {username} already exists")
                    flash('Username already exists.', 'danger')
                else:
                    app.logger.warning(f"Email {email} already exists")
                    flash('Email already exists.', 'danger')
                return render_template('register.html')
            
            # Create new user
            try:
                new_user = User(
                    username=username,
                    email=email,
                    is_parent=(account_type == 'parent'),
                    is_child=(account_type == 'child'),
                    role=UserRole.PARENT if account_type == 'parent' else UserRole.CHILD,
                    created_at=datetime.utcnow()
                )
                new_user.set_password(password)
                
                app.logger.info(f"Created new user object for {username}")
                
                # Add and commit in a transaction
                db.session.begin_nested()
                db.session.add(new_user)
                db.session.commit()
                
                app.logger.info(f"Successfully saved user {username} to database")
                
                # Log the user in
                login_user(new_user)
                
                # Create welcome activity
                activity = Activity(
                    user_id=new_user.id,
                    activity_type="LOGIN",
                    message=f"Welcome to Kids Wishlist, {new_user.username}! 🎉",
                    emoji="👋",
                    timestamp=datetime.utcnow()
                )
                db.session.add(activity)
                db.session.commit()
                
                app.logger.info(f"Registration complete for {username}")
                flash('Registration successful! Welcome to Kids Wishlist!', 'success')
                return redirect(url_for('dashboard'))
                
            except SQLAlchemyError as e:
                db.session.rollback()
                app.logger.error(f"Database error during user creation: {str(e)}")
                flash('An error occurred while creating your account. Please try again.', 'danger')
                return render_template('register.html')
                
        except Exception as e:
            app.logger.error(f"Unexpected error during registration: {str(e)}")
            flash('An unexpected error occurred. Please try again.', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/register_child', methods=['GET', 'POST'])
@login_required
def register_child():
    if current_user.is_child:
        flash('Only parents can register child accounts.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register_child'))

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register_child'))

        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        base_email = current_user.email.split('@')
        child_email = f"{base_email[0]}+child_{username}_{timestamp}@{base_email[1]}"

        child = User(
            username=username,
            email=child_email,
            is_child=True,
            parent_id=current_user.id
        )
        child.set_password(password)
        db.session.add(child)
        
        try:
            db.session.commit()
            flash(f'Successfully registered {username}!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the child account. Please try again.', 'error')
            return redirect(url_for('register_child'))

    return render_template('register_child.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/w/<share_code>')
def public_wishlist(share_code):
    wishlist = Wishlist.query.filter_by(share_code=share_code).first_or_404()
    
    # Get the theme details
    theme = get_theme_by_id(wishlist.theme)
    
    # Group items by priority
    wishlist_items = {
        'HIGH': [],
        'MEDIUM': [],
        'LOW': []
    }
    
    for item in wishlist.items:
        if item.priority:
            wishlist_items[item.priority.value].append(item)
    
    # Sort items within each priority group by creation date
    for priority in wishlist_items:
        wishlist_items[priority].sort(key=lambda x: x.created_at, reverse=True)
    
    return render_template('public_wishlist.html', 
                         wishlist=wishlist, 
                         wishlist_items=wishlist_items,
                         theme=theme)

@app.route('/w/<share_code>/claim/<int:item_id>', methods=['POST'])
def claim_public_item(share_code, item_id):
    wishlist = Wishlist.query.filter_by(share_code=share_code).first_or_404()
    item = WishlistItem.query.get_or_404(item_id)
    
    # Verify the item belongs to this wishlist
    if item.wishlist_id != wishlist.id:
        abort(404)
    
    if item.purchased:
        flash('This item has already been claimed.', 'warning')
        return redirect(url_for('public_wishlist', share_code=share_code))
    
    purchaser_name = request.form.get('purchaser_name')
    if not purchaser_name:
        flash('Please provide your name.', 'error')
        return redirect(url_for('public_wishlist', share_code=share_code))
    
    item.purchased = True
    item.purchased_by = purchaser_name
    item.purchased_at = datetime.utcnow()
    
    # Create an activity record
    activity = Activity(
        user_id=wishlist.user_id,
        activity_type='ITEM_CLAIMED',
        message=f'{purchaser_name} has claimed "{item.name}"',
        emoji='🎁',
        related_wishlist_id=wishlist.id,
        related_item_id=item.id,
        is_public=True
    )
    
    # Create a notification for the wishlist owner
    notification = Notification(
        user_id=wishlist.user_id,
        title='Item Claimed!',
        message=f'{purchaser_name} has claimed "{item.name}" from your wishlist.',
        type='ITEM_CLAIMED',
        action_url=url_for('public_wishlist', share_code=share_code)
    )
    
    db.session.add(activity)
    db.session.add(notification)
    db.session.commit()
    
    flash(f'You have successfully claimed "{item.name}". Thank you!', 'success')
    return redirect(url_for('public_wishlist', share_code=share_code))

@app.route('/wishlist/<int:wishlist_id>')
@login_required
def manage_wishlist(wishlist_id):
    wishlist = Wishlist.query.get_or_404(wishlist_id)
    
    # Check if the user owns this wishlist
    if wishlist.user_id != current_user.id and not current_user.role == UserRole.ADMIN:
        abort(403)
    
    return render_template('manage_wishlist.html', wishlist=wishlist)

@app.route('/wishlist/<int:wishlist_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_wishlist(wishlist_id):
    wishlist = Wishlist.query.get_or_404(wishlist_id)
    # Allow both the wishlist owner and their parent to edit
    if wishlist.user_id != current_user.id and not (current_user.is_parent and current_user.id == User.query.get(wishlist.user_id).parent_id):
        abort(403)
        
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        theme = request.form.get('theme')
        occasion = request.form.get('occasion')
        
        if title:
            wishlist.title = title
        if description:
            wishlist.description = description
        if theme:
            wishlist.theme = theme
        if occasion:
            wishlist.occasion = occasion
            
            # Handle occasion-specific details
            if occasion == 'birthday' and request.form.get('birthday_date'):
                try:
                    wishlist.occasion_date = datetime.strptime(request.form.get('birthday_date'), '%Y-%m-%d')
                    if request.form.get('turning_age'):
                        wishlist.turning_age = int(request.form.get('turning_age'))
                except (ValueError, TypeError) as e:
                    app.logger.error(f"Error parsing birthday details: {str(e)}")
                    
            elif occasion == 'graduation' and request.form.get('graduation_date'):
                try:
                    wishlist.occasion_date = datetime.strptime(request.form.get('graduation_date'), '%Y-%m-%d')
                    wishlist.school_name = request.form.get('school_name')
                except ValueError as e:
                    app.logger.error(f"Error parsing graduation date: {str(e)}")

        try:
            db.session.commit()
            
            # Create activity
            activity = Activity(
                user_id=current_user.id,
                message=f"Updated wishlist: {wishlist.title}",
                emoji="✏️",
                related_wishlist_id=wishlist.id
            )
            db.session.add(activity)
            db.session.commit()
            
            flash('Wishlist updated successfully!', 'success')
            return redirect(url_for('manage_wishlist', wishlist_id=wishlist_id))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating wishlist: {str(e)}")
            flash('Error updating wishlist. Please try again.', 'error')
            
    return render_template('edit_wishlist.html', wishlist=wishlist)

@app.route('/wishlist/<int:wishlist_id>/add_item', methods=['GET', 'POST'])
@login_required
def add_wishlist_item(wishlist_id):
    wishlist = Wishlist.query.get_or_404(wishlist_id)
    # Allow both the wishlist owner and their parent to add items
    if wishlist.user_id != current_user.id and not (current_user.is_parent and current_user.id == User.query.get(wishlist.user_id).parent_id):
        abort(403)
        
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        url = request.form.get('url')
        priority = request.form.get('priority', 'MEDIUM')
        
        if not name:
            flash('Item name is required!', 'error')
            return redirect(url_for('add_wishlist_item', wishlist_id=wishlist_id))
            
        try:
            # Handle image uploads
            images = request.files.getlist('images')
            saved_images = save_uploaded_images(images)
            image_urls = ','.join(saved_images) if saved_images else None
            
            # Create new wishlist item
            item = WishlistItem(
                name=name,
                description=description,
                url=url,
                priority=priority,
                wishlist_id=wishlist_id,
                image_url=image_urls
            )
            db.session.add(item)
            
            # Create activity with proper activity type
            activity = Activity(
                user_id=current_user.id,
                message=f"Added item '{name}' to wishlist: {wishlist.title}",
                emoji="➕",
                related_wishlist_id=wishlist.id,
                activity_type="ADD_ITEM",
                is_public=True,
                timestamp=datetime.utcnow()
            )
            db.session.add(activity)
            
            db.session.commit()
            flash('Item added successfully!', 'success')
            return redirect(url_for('manage_wishlist', wishlist_id=wishlist_id))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error adding wishlist item: {str(e)}")
            flash('Error adding item to wishlist. Please try again.', 'error')
            
    return render_template('add_wishlist_item.html', wishlist=wishlist)

@app.route('/wishlist/item/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_wishlist_item(item_id):
    item = WishlistItem.query.get_or_404(item_id)
    wishlist = Wishlist.query.get(item.wishlist_id)
    
    # Allow both the wishlist owner and their parent to edit items
    if wishlist.user_id != current_user.id and not (current_user.is_parent and current_user.id == User.query.get(wishlist.user_id).parent_id):
        abort(403)
        
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        url = request.form.get('url')
        priority = request.form.get('priority')
        
        if name:
            item.name = name
        if description:
            item.description = description
        if url:
            item.url = url
        if priority:
            item.priority = priority
            
        try:
            # Create activity
            activity = Activity(
                user_id=current_user.id,
                message=f"Updated item '{item.name}' in wishlist: {wishlist.title}",
                emoji="✏️",
                related_wishlist_id=wishlist.id
            )
            db.session.add(activity)
            
            db.session.commit()
            flash('Item updated successfully!', 'success')
            return redirect(url_for('manage_wishlist', wishlist_id=item.wishlist_id))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating wishlist item: {str(e)}")
            flash('Error updating item. Please try again.', 'error')
            
    return render_template('edit_wishlist_item.html', item=item, wishlist=wishlist)

@app.route('/wishlist/item/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_wishlist_item(item_id):
    item = WishlistItem.query.get_or_404(item_id)
    wishlist = Wishlist.query.get(item.wishlist_id)
    
    # Allow both the wishlist owner and their parent to delete items
    if wishlist.user_id != current_user.id and not (current_user.is_parent and current_user.id == User.query.get(wishlist.user_id).parent_id):
        abort(403)
        
    try:
        # Create activity before deleting the item
        activity = Activity(
            user_id=current_user.id,
            message=f"Removed item '{item.name}' from wishlist: {wishlist.title}",
            emoji="🗑️",
            related_wishlist_id=wishlist.id
        )
        db.session.add(activity)
        
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting wishlist item: {str(e)}")
        flash('Error deleting item. Please try again.', 'error')
        
    return redirect(url_for('manage_wishlist', wishlist_id=item.wishlist_id))

@app.route('/wishlist/<int:wishlist_id>/customize-share', methods=['POST'])
@login_required
def customize_share_url(wishlist_id):
    wishlist = Wishlist.query.get_or_404(wishlist_id)
    
    if wishlist.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    custom_url = request.form.get('custom_url', '').strip()
    if not custom_url:
        return jsonify({'success': False, 'message': 'Custom URL cannot be empty'}), 400
    
    success, message = wishlist.set_custom_share_url(custom_url)
    if success:
        db.session.commit()
        share_url = url_for('view_shared_wishlist', custom_url=wishlist.custom_share_url, _external=True)
        return jsonify({
            'success': True, 
            'message': message,
            'share_url': share_url
        })
    return jsonify({'success': False, 'message': message}), 400

@app.route('/share/<custom_url>')
def view_shared_wishlist(custom_url):
    wishlist = Wishlist.query.filter_by(custom_share_url=custom_url).first_or_404()
    return render_template('shared_wishlist.html', wishlist=wishlist)

@app.route('/wishlist/<int:wishlist_id>/share')
@login_required
def get_share_info(wishlist_id):
    wishlist = Wishlist.query.get_or_404(wishlist_id)
    
    if wishlist.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    share_code = wishlist.generate_share_code()
    db.session.commit()
    
    share_data = {
        'share_code': share_code,
        'custom_url': wishlist.custom_share_url,
        'share_urls': {
            'code': url_for('public_wishlist', share_code=share_code, _external=True),
            'custom': url_for('view_shared_wishlist', custom_url=wishlist.custom_share_url, _external=True) if wishlist.custom_share_url else None
        }
    }
    
    return jsonify({'success': True, 'data': share_data})

@app.route('/parent/child/<int:child_id>')
@login_required
def parent_view_child(child_id):
    if not current_user.is_parent:
        flash('Access denied. Parent account required.', 'error')
        return redirect(url_for('dashboard'))
    
    child = User.query.filter_by(id=child_id, parent_id=current_user.id).first_or_404()
    return render_template('child_details.html', child=child)

@app.route('/parent/child/<int:child_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_child(child_id):
    child = User.query.filter_by(id=child_id, parent_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        child.username = request.form['username']
        if 'email' in request.form:
            child.email = request.form['email']
        if request.form.get('password'):
            child.set_password(request.form['password'])
            
        db.session.commit()
        flash('Child account updated successfully', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('edit_child.html', child=child)

@app.route('/parent/child/<int:child_id>/toggle-status', methods=['POST'])
@login_required
def toggle_child_status(child_id):
    child = User.query.filter_by(id=child_id, parent_id=current_user.id).first_or_404()
    child.is_child = not child.is_child
    db.session.commit()
    return jsonify({'success': True, 'message': f"Child account {'activated' if child.is_child else 'deactivated'} successfully"})

@app.route('/add_child', methods=['GET', 'POST'])
@login_required
def add_child():
    if current_user.is_child:
        flash('Only parents can add child accounts.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')  

        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('add_child'))

        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        base_email = current_user.email.split('@')
        child_email = f"{base_email[0]}+child_{username}_{timestamp}@{base_email[1]}"

        child = User(
            username=username,
            email=child_email,
            is_child=True,
            parent_id=current_user.id
        )

        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        child.set_password(password)

        db.session.add(child)
        try:
            db.session.commit()
            flash(f'Child account created successfully! Username: {username}, Password: {password}', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the child account. Please try again.', 'error')
            return redirect(url_for('add_child'))

    return render_template('add_child.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('policies/privacy_policy.html')

@app.route('/terms')
def terms():
    return render_template('policies/terms.html')

@app.route('/kids-safety')
def kids_safety():
    return render_template('policies/kids_safety.html')

@app.route('/parents-guide')
def parents_guide():
    return render_template('policies/parents_guide.html')

@app.route('/cookie-policy')
def cookie_policy():
    return render_template('policies/cookie_policy.html')

@app.route('/admin/flush_data', methods=['GET'])
def flush_data():
    try:
        app.logger.info("Starting database flush...")
        
        # Step 1: Close all database connections
        try:
            db.session.remove()
            db.session.close_all()
            db.engine.dispose()
            app.logger.info("Database connections closed successfully")
        except Exception as e:
            app.logger.error(f"Error closing database connections: {str(e)}")
            raise
        
        # Step 2: Remove database files
        db_files = [
            '/Users/antoniosmith/CascadeProjects/kidswishlist/instance/kidswishlist.db',
            '/Users/antoniosmith/CascadeProjects/kidswishlist/instance/wishlist.db',
            '/Users/antoniosmith/CascadeProjects/kidswishlist/wishlist.db'
        ]
        
        for db_path in db_files:
            try:
                if os.path.exists(db_path):
                    os.remove(db_path)
                    app.logger.info(f"Successfully removed database file: {db_path}")
            except Exception as e:
                app.logger.error(f"Error removing database file {db_path}: {str(e)}")
                # Continue even if one file fails to delete
        
        # Step 3: Clear Flask session
        try:
            session.clear()
            app.logger.info("Flask session cleared")
        except Exception as e:
            app.logger.error(f"Error clearing Flask session: {str(e)}")
            raise
        
        # Step 4: Create instance directory if it doesn't exist
        try:
            instance_path = '/Users/antoniosmith/CascadeProjects/kidswishlist/instance'
            if not os.path.exists(instance_path):
                os.makedirs(instance_path)
                app.logger.info(f"Created instance directory: {instance_path}")
        except Exception as e:
            app.logger.error(f"Error creating instance directory: {str(e)}")
            raise
        
        # Step 5: Initialize new database
        try:
            with app.app_context():
                db.create_all()
                db.session.commit()
                app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
            raise
        
        app.logger.info("Database flush completed successfully")
        flash('All data has been flushed successfully!', 'success')
        
    except Exception as e:
        app.logger.error(f"Critical error during database flush: {str(e)}")
        flash('Error flushing data. Please check the logs.', 'danger')
        db.session.rollback()
    
    return redirect(url_for('index'))

@app.route('/demo')
def demo_page():
    """Demo page showcasing different wishlist themes and features."""
    demo_wishlists = get_demo_wishlists()
    return render_template('demo.html', demo_wishlists=demo_wishlists)

@app.route('/demo/<wishlist_id>')
def view_demo_wishlist(wishlist_id):
    """View a demo wishlist."""
    demo_wishlists = get_demo_wishlists()
    if wishlist_id not in demo_wishlists:
        flash('Demo wishlist not found!', 'error')
        return redirect(url_for('demo_page'))
    
    wishlist = DemoWishlist(demo_wishlists[wishlist_id])
    
    return render_template('view_demo_wishlist.html', 
                         wishlist=wishlist)

if __name__ == '__main__':
    print("Starting server on http://localhost:3000")
    with app.app_context():
        db.create_all()
    app.run(port=3000, debug=True)
