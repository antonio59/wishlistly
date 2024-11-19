"""initial_migration

Revision ID: bba661ce3b2e
Revises: 
Create Date: 2024-11-18 16:33:12.709140

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bba661ce3b2e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('role', sa.Enum('ADMIN', 'PARENT', 'CHILD', 'GUEST', name='userrole'), nullable=True),
    sa.Column('is_parent', sa.Boolean(), nullable=True),
    sa.Column('is_child', sa.Boolean(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('email_verified', sa.Boolean(), nullable=True),
    sa.Column('avatar_url', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('message', sa.String(length=500), nullable=False),
    sa.Column('type', sa.String(length=50), nullable=False),
    sa.Column('read', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('action_url', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('wishlist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('theme', sa.String(length=50), nullable=True),
    sa.Column('occasion', sa.String(length=100), nullable=True),
    sa.Column('occasion_date', sa.DateTime(), nullable=True),
    sa.Column('turning_age', sa.Integer(), nullable=True),
    sa.Column('school_name', sa.String(length=200), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('share_code', sa.String(length=10), nullable=True),
    sa.Column('custom_url', sa.String(length=50), nullable=True),
    sa.Column('is_public', sa.Boolean(), nullable=True),
    sa.Column('allow_comments', sa.Boolean(), nullable=True),
    sa.Column('total_items', sa.Integer(), nullable=True),
    sa.Column('total_purchased', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('custom_url'),
    sa.UniqueConstraint('share_code')
    )
    op.create_table('wishlist_follower',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('wishlist_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['wishlist_id'], ['wishlist.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'wishlist_id', name='unique_follower')
    )
    op.create_table('wishlist_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('url', sa.String(length=500), nullable=True),
    sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', name='prioritylevel'), nullable=True),
    sa.Column('purchased', sa.Boolean(), nullable=True),
    sa.Column('purchased_by', sa.String(length=100), nullable=True),
    sa.Column('purchased_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('wishlist_id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(length=500), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['wishlist_id'], ['wishlist.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('activity',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('activity_type', sa.String(length=50), nullable=False),
    sa.Column('message', sa.String(length=500), nullable=False),
    sa.Column('emoji', sa.String(length=10), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('related_wishlist_id', sa.Integer(), nullable=True),
    sa.Column('related_item_id', sa.Integer(), nullable=True),
    sa.Column('is_public', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['related_item_id'], ['wishlist_item.id'], ),
    sa.ForeignKeyConstraint(['related_wishlist_id'], ['wishlist.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('wishlist_id', sa.Integer(), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['wishlist_item.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['comment.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['wishlist_id'], ['wishlist.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('price_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['wishlist_item.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('price_history')
    op.drop_table('comment')
    op.drop_table('activity')
    op.drop_table('wishlist_item')
    op.drop_table('wishlist_follower')
    op.drop_table('wishlist')
    op.drop_table('notification')
    op.drop_table('user')
    # ### end Alembic commands ###