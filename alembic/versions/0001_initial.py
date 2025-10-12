"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2025-10-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )

    op.create_table(
        'categories',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=120), nullable=False),
        sa.UniqueConstraint('name', name='uq_categories_name'),
        sa.UniqueConstraint('slug', name='uq_categories_slug'),
    )

    op.create_table(
        'products',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('sku', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(12,2), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT'),
        sa.UniqueConstraint('sku', name='uq_products_sku'),
        sa.CheckConstraint('price >= 0', name='ck_product_price_non_negative'),
        sa.CheckConstraint('stock >= 0', name='ck_product_stock_non_negative'),
    )
    op.create_index('ix_products_category', 'products', ['category_id'])

    op.create_table(
        'tags',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.UniqueConstraint('name', name='uq_tags_name'),
    )

    op.create_table(
        'product_tags',
        sa.Column('product_id', sa.BigInteger(), sa.ForeignKey('products.id', ondelete='CASCADE'), primary_key=True, nullable=False),
        sa.Column('tag_id', sa.BigInteger(), sa.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    )

    op.create_table(
        'orders',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('total_amount', sa.Numeric(12,2), nullable=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint('total_amount >= 0', name='ck_order_total_non_negative'),
    )

    op.create_table(
        'order_items',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('order_id', sa.BigInteger(), nullable=False),
        sa.Column('product_id', sa.BigInteger(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(12,2), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
        sa.CheckConstraint('quantity > 0', name='ck_orderitem_quantity_positive'),
        sa.CheckConstraint('unit_price >= 0', name='ck_orderitem_unit_price_non_negative'),
    )
    op.create_index('ix_order_items_order', 'order_items', ['order_id'])

    op.create_table(
        'reviews',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('product_id', sa.BigInteger(), nullable=True),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('product_id', 'user_id', name='uq_review_product_user'),
        sa.CheckConstraint('rating BETWEEN 1 AND 5', name='ck_review_rating_range'),
    )

def downgrade():
    op.drop_table('reviews')
    op.drop_index('ix_order_items_order', table_name='order_items')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('product_tags')
    op.drop_table('tags')
    op.drop_index('ix_products_category', table_name='products')
    op.drop_table('products')
    op.drop_table('categories')
    op.drop_table('users')
