from sqlalchemy import (
    Column, BigInteger, String, Text, Boolean, Numeric, Integer, ForeignKey,
    TIMESTAMP, func, Table, CheckConstraint, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

product_tags = Table(
    "product_tags",
    Base.metadata,
    Column("product_id", BigInteger, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", BigInteger, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")

class Category(Base):
    __tablename__ = "categories"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(120), nullable=False, unique=True)

    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sku = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(12,2), nullable=False)
    stock = Column(Integer, nullable=False)
    category_id = Column(BigInteger, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    category = relationship("Category", back_populates="products")
    tags = relationship("Tag", secondary=product_tags, back_populates="products")
    reviews = relationship("Review", back_populates="product")

    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_product_price_non_negative"),
        CheckConstraint("stock >= 0", name="ck_product_stock_non_negative"),
        Index("ix_products_category", "category_id"),
    )

class Tag(Base):
    __tablename__ = "tags"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

    products = relationship("Product", secondary=product_tags, back_populates="tags")

class Order(Base):
    __tablename__ = "orders"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(30), nullable=False, default="pending")
    total_amount = Column(Numeric(12,2), nullable=False, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="ck_order_total_non_negative"),
    )

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12,2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_orderitem_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="ck_orderitem_unit_price_non_negative"),
        Index("ix_order_items_order", "order_id"),
    )

class Review(Base):
    __tablename__ = "reviews"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"))
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_review_rating_range"),
        UniqueConstraint("product_id", "user_id", name="uq_review_product_user"),
    )
