from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from models.user import User
from models.wishlist import Wishlist, WishlistItem
from models.activity import Activity
from models.db import db
from datetime import datetime
from forms.wishlist import WishlistForm, WishlistItemForm

wishlist = Blueprint('wishlist', __name__)

@wishlist.route('/create', methods=['GET', 'POST'])
@login_required
def create_wishlist():
    form = WishlistForm()
    
    if form.validate_on_submit():
        new_wishlist = Wishlist(
            name=form.name.data,
            description=form.description.data,
            occasion=form.occasion.data,
            event_date=form.event_date.data,
            theme=form.theme.data,
            is_public=form.is_public.data,
            user_id=current_user.id
        )
        
        db.session.add(new_wishlist)
        
        # Log activity
        activity = Activity(
            user_id=current_user.id,
            action='create_wishlist',
            details=f'Created wishlist: {new_wishlist.name}'
        )
        db.session.add(activity)
        
        try:
            db.session.commit()
            flash('Wishlist created successfully!', 'success')
            return redirect(url_for('wishlist.view_wishlist', wishlist_id=new_wishlist.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your wishlist. Please try again.', 'error')
            return redirect(url_for('wishlist.create_wishlist'))
    
    return render_template('create_wishlist.html', form=form)

@wishlist.route('/<int:wishlist_id>')
def view_wishlist(wishlist_id):
    wishlist = Wishlist.query.get_or_404(wishlist_id)
    
    # Check if user can view this wishlist
    if not wishlist.is_public and (not current_user.is_authenticated or 
        (current_user.id != wishlist.user_id and 
         not (current_user.is_parent and wishlist.owner.parent_id == current_user.id))):
        flash('You do not have permission to view this wishlist', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('view_wishlist.html', wishlist=wishlist)

@wishlist.route('/<int:wishlist_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_wishlist(wishlist_id):
    wishlist = Wishlist.query.get_or_404(wishlist_id)
    
    # Check if user can edit this wishlist
    if current_user.id != wishlist.user_id and not (current_user.is_parent and wishlist.owner.parent_id == current_user.id):
        flash('You do not have permission to edit this wishlist', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        wishlist.name = request.form.get('name', wishlist.name)
        wishlist.description = request.form.get('description')
        wishlist.occasion = request.form.get('occasion')
        wishlist.theme = request.form.get('theme', 'default')
        wishlist.is_public = request.form.get('is_public', True)
        
        event_date = request.form.get('event_date')
        if event_date:
            try:
                wishlist.event_date = datetime.strptime(event_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD', 'error')
                return redirect(url_for('wishlist.edit_wishlist', wishlist_id=wishlist_id))
        
        # Log activity
        activity = Activity(
            user_id=current_user.id,
            action='edit_wishlist',
            details=f'Edited wishlist: {wishlist.name}'
        )
        db.session.add(activity)
        
        try:
            db.session.commit()
            flash('Wishlist updated successfully!', 'success')
            return redirect(url_for('wishlist.view_wishlist', wishlist_id=wishlist_id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your wishlist. Please try again.', 'error')
    
    return render_template('edit_wishlist.html', wishlist=wishlist)

@wishlist.route('/<int:wishlist_id>/delete', methods=['POST'])
@login_required
def delete_wishlist(wishlist_id):
    wishlist = Wishlist.query.get_or_404(wishlist_id)
    
    # Check if user can delete this wishlist
    if current_user.id != wishlist.user_id and not (current_user.is_parent and wishlist.owner.parent_id == current_user.id):
        flash('You do not have permission to delete this wishlist', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Log activity before deletion
        activity = Activity(
            user_id=current_user.id,
            action='delete_wishlist',
            details=f'Deleted wishlist: {wishlist.name}'
        )
        db.session.add(activity)
        
        db.session.delete(wishlist)
        db.session.commit()
        flash('Wishlist deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the wishlist', 'error')
    
    return redirect(url_for('main.dashboard'))

@wishlist.route('/<int:wishlist_id>/items/add', methods=['POST'])
@login_required
def add_item(wishlist_id):
    wishlist = Wishlist.query.get_or_404(wishlist_id)
    
    # Check if user can add items to this wishlist
    if current_user.id != wishlist.user_id and not (current_user.is_parent and wishlist.owner.parent_id == current_user.id):
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Item name is required'}), 400
    
    new_item = WishlistItem(
        name=data['name'],
        description=data.get('description'),
        url=data.get('url'),
        price=data.get('price'),
        priority=data.get('priority', 'WOULD_LIKE'),
        wishlist_id=wishlist_id
    )
    
    db.session.add(new_item)
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        action='add_wishlist_item',
        details=f'Added item to wishlist: {wishlist.name}'
    )
    db.session.add(activity)
    
    try:
        db.session.commit()
        return jsonify(new_item.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add item'}), 500

@wishlist.route('/items/<int:item_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_item(item_id):
    item = WishlistItem.query.get_or_404(item_id)
    wishlist = item.wishlist
    
    # Check if user can manage this item
    if current_user.id != wishlist.user_id and not (current_user.is_parent and wishlist.owner.parent_id == current_user.id):
        return jsonify({'error': 'Permission denied'}), 403
    
    if request.method == 'DELETE':
        try:
            # Log activity before deletion
            activity = Activity(
                user_id=current_user.id,
                action='delete_wishlist_item',
                details=f'Deleted item from wishlist: {wishlist.name}'
            )
            db.session.add(activity)
            
            db.session.delete(item)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to delete item'}), 500
    
    # Handle PUT (update)
    data = request.get_json()
    
    try:
        if 'name' in data:
            item.name = data['name']
        if 'description' in data:
            item.description = data['description']
        if 'url' in data:
            item.url = data['url']
        if 'price' in data:
            item.price = data['price']
        if 'priority' in data:
            item.priority = data['priority']
        if 'is_purchased' in data:
            item.is_purchased = data['is_purchased']
            if item.is_purchased:
                item.purchased_by = current_user.username
        
        # Log activity
        activity = Activity(
            user_id=current_user.id,
            action='update_wishlist_item',
            details=f'Updated item in wishlist: {wishlist.name}'
        )
        db.session.add(activity)
        
        db.session.commit()
        return jsonify(item.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update item'}), 500
