"""
Migration script to update priority levels from HIGH/MEDIUM/LOW to MUST_HAVE/WOULD_LOVE/NICE_TO_HAVE
"""
from flask import Flask
from models import db, WishlistItem

def upgrade():
    # Create a mapping of old priorities to new ones
    priority_mapping = {
        'HIGH': 'MUST_HAVE',
        'MEDIUM': 'WOULD_LOVE',
        'LOW': 'NICE_TO_HAVE'
    }
    
    try:
        # Get all wishlist items
        items = WishlistItem.query.all()
        
        # Update each item's priority
        for item in items:
            if hasattr(item, 'priority') and item.priority and item.priority.value in priority_mapping:
                # Update the priority using raw SQL to avoid enum validation
                db.session.execute(
                    'UPDATE wishlist_item SET priority = :new_priority WHERE id = :item_id',
                    {
                        'new_priority': priority_mapping[item.priority.value],
                        'item_id': item.id
                    }
                )
        
        # Commit the changes
        db.session.commit()
        print("Successfully updated priority levels for all wishlist items")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating priority levels: {str(e)}")
        raise

def downgrade():
    # Create a mapping of new priorities to old ones
    priority_mapping = {
        'MUST_HAVE': 'HIGH',
        'WOULD_LOVE': 'MEDIUM',
        'NICE_TO_HAVE': 'LOW'
    }
    
    try:
        # Get all wishlist items
        items = WishlistItem.query.all()
        
        # Update each item's priority
        for item in items:
            if hasattr(item, 'priority') and item.priority and item.priority.value in priority_mapping:
                # Update the priority using raw SQL to avoid enum validation
                db.session.execute(
                    'UPDATE wishlist_item SET priority = :new_priority WHERE id = :item_id',
                    {
                        'new_priority': priority_mapping[item.priority.value],
                        'item_id': item.id
                    }
                )
        
        # Commit the changes
        db.session.commit()
        print("Successfully reverted priority levels for all wishlist items")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error reverting priority levels: {str(e)}")
        raise
