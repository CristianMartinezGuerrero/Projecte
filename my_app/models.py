from . import db_manager as db
from datetime import datetime

# Taula categories
class categories(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)

# Taula users
class users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Taula products
class products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Taula orders
class orders(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('product_id', 'buyer_id', name='uc_product_buyer'),
    )

# Taula confirmed_orders
class confirmed_orders(db.Model):
    __tablename__ = "confirmed_orders"
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
