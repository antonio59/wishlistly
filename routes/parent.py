from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models.user import User
from models.sharing import SharingRequest, Notification
from models.wishlist import Wishlist
from models.db import db
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

parent = Blueprint('parent', __name__)

def calculate_age(born):
    today = date.today()
    return relativedelta(today, born).years

@parent.route('/parent-dashboard')
@login_required
def dashboard():
    if not current_user.is_parent:
        abort(403)
    
    children = User.query.filter_by(parent_id=current_user.id).all()
    pending_requests = SharingRequest.query.filter_by(
        parent_id=current_user.id, 
        status='pending'
    ).all()
    
    # Get recent activity for all children
    child_activities = []
    for child in children:
        activities = Wishlist.query.filter_by(user_id=child.id)\
            .order_by(Wishlist.updated_at.desc())\
            .limit(5).all()
        child_activities.extend(activities)
    
    # Sort activities by date
    child_activities.sort(key=lambda x: x.updated_at, reverse=True)
    
    return render_template('parent/dashboard.html',
                         children=children,
                         activities=child_activities[:10],
                         pending_requests=pending_requests)

@parent.route('/child/<int:child_id>/manage')
@login_required
def manage_child(child_id):
    if not current_user.is_parent:
        abort(403)
    
    child = User.query.get_or_404(child_id)
    if child.parent_id != current_user.id:
        abort(403)
    
    return render_template('parent/manage_child.html', child=child)

@parent.route('/child/<int:child_id>/settings', methods=['POST'])
@login_required
def update_child_settings(child_id):
    if not current_user.is_parent:
        abort(403)
    
    child = User.query.get_or_404(child_id)
    if child.parent_id != current_user.id:
        abort(403)
    
    # Update child settings
    child.requires_parent_approval = 'requires_approval' in request.form
    child.can_manage_account = 'can_manage_account' in request.form
    child.sharing_enabled = 'sharing_enabled' in request.form
    
    # Check age for account management permissions
    if child.date_of_birth:
        age = calculate_age(child.date_of_birth)
        if age < 13:
            child.requires_parent_approval = True
            child.can_manage_account = False
    
    db.session.commit()
    flash('Child account settings updated successfully!', 'success')
    return redirect(url_for('parent.manage_child', child_id=child_id))

@parent.route('/sharing-request/<int:request_id>/<action>')
@login_required
def handle_sharing_request(request_id, action):
    if not current_user.is_parent:
        abort(403)
    
    sharing_request = SharingRequest.query.get_or_404(request_id)
    if sharing_request.parent_id != current_user.id:
        abort(403)
    
    if action == 'approve':
        sharing_request.status = 'approved'
        message = f"Your wishlist sharing request has been approved by your parent."
    elif action == 'reject':
        sharing_request.status = 'rejected'
        message = f"Your wishlist sharing request has been rejected by your parent."
    else:
        abort(400)
    
    # Create notification for child
    notification = Notification(
        user_id=sharing_request.child_id,
        type='sharing_request_update',
        message=message,
        sharing_request_id=sharing_request.id
    )
    db.session.add(notification)
    db.session.commit()
    
    flash(f'Sharing request {action}d successfully!', 'success')
    return redirect(url_for('parent.dashboard'))

@parent.route('/notifications')
@login_required
def notifications():
    if not current_user.is_parent:
        abort(403)
    
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        read=False
    ).order_by(Notification.created_at.desc()).all()
    
    return render_template('parent/notifications.html', notifications=notifications)
