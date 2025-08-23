"""add item fields

Revision ID: 002_add_item_fields
Revises: 001_initial
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_item_fields'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to items table
    op.add_column('items', sa.Column('category', sa.String(), nullable=True))
    op.add_column('items', sa.Column('stock_quantity', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('items', sa.Column('image_url', sa.String(), nullable=True))
    op.add_column('items', sa.Column('rating', sa.Float(), nullable=True))
    op.add_column('items', sa.Column('tags', sa.String(), nullable=True))
    
    # Create index on category for better performance
    op.create_index('ix_items_category', 'items', ['category'])


def downgrade() -> None:
    # Remove index
    op.drop_index('ix_items_category', table_name='items')
    
    # Remove columns
    op.drop_column('items', 'tags')
    op.drop_column('items', 'rating')
    op.drop_column('items', 'image_url')
    op.drop_column('items', 'stock_quantity')
    op.drop_column('items', 'category')