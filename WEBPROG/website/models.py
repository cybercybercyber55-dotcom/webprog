from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import date


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(150))

    # rename boolean flag to avoid colliding with the property name
    is_admin_flag = db.Column(db.Boolean, default=False)

    notes = db.relationship('Note')
    devices = db.relationship('Device', backref='owner', lazy=True)

    # role string column (admin / user)
    role = db.Column(db.String(20), nullable=False, default='user')

    @property
    def is_admin(self):
        """
        Compatibility property:
        - if the role == 'admin' -> True
        - otherwise falls back to boolean flag (legacy users)
        """
        # prefer role-based check
        if self.role is not None:
            return self.role == 'admin'
        # fallback for legacy flag (if role missing)
        return bool(getattr(self, 'is_admin_flag', False))

    # optional helper for templates
    @property
    def is_admin_prop(self):
        return self.role == 'admin'


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)        # e.g. "Dell Laptop"
    category = db.Column(db.String(100), nullable=False)    # e.g. "Laptop", "Phone"
    status = db.Column(db.String(50), nullable=False, default='Available')  # "Available", "In Use", "Under Repair"
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # who it’s assigned to (can be NULL)
    location = db.Column(db.String(150))                   # e.g. "Office 1", "Home", etc.
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())

# class Category(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(150), unique=True, nullable=False)
#     created_at = db.Column(db.DateTime(timezone=True), default=func.now())

#     products = db.relationship('Product', backref='category', lazy=True)

# class Product(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(150), nullable=False)
#     price = db.Column(db.Numeric(10, 2), nullable=False)
#     quantity = db.Column(db.Integer, nullable=False, default=0)
#     image_filename = db.Column(db.String(255))
#     category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
#     created_at = db.Column(db.DateTime(timezone=True), default=func.now())

# class Customer(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(150), nullable=False)
#     address = db.Column(db.String(255), nullable=False)
#     email = db.Column(db.String(150), nullable=False)
#     contact = db.Column(db.String(50), nullable=False)
#     created_at = db.Column(db.DateTime(timezone=True), default=func.now())


class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(255))
    email = db.Column(db.String(150))
    contact = db.Column(db.String(50))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    purchases = db.relationship(
        "Purchase",
        back_populates="supplier",
        cascade="all, delete-orphan"
        )

## for outgoing Product
class Outgoing(db.Model):
    __tablename__ = "outgoing"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False, server_default=func.current_date())
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # relationships
    product = db.relationship("Product", back_populates="outgoings")
    customer = db.relationship("Customer", back_populates="outgoings")


# Make sure Product and Customer have back_populates

class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Numeric(10, 2))
    quantity = db.Column(db.Integer, default=0)
    image_filename = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # category = db.relationship("Category", back_populates="products")
    outgoings = db.relationship("Outgoing", back_populates="product", cascade="all, delete-orphan")
    purchases = db.relationship(
        "Purchase",
        back_populates="product",
        cascade="all, delete-orphan"
        )


class Customer(db.Model):
    __tablename__ = "customer"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(255))
    email = db.Column(db.String(150))
    contact = db.Column(db.String(50))

    outgoings = db.relationship("Outgoing", back_populates="customer", cascade="all, delete-orphan")

class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)

    # KEEP this
    products = db.relationship(
        "Product",
        backref="category",
        cascade="all, delete-orphan"
    )

class Purchase(db.Model):
    __tablename__ = "purchase"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey("supplier.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # relationships
    product = db.relationship("Product", back_populates="purchases")
    supplier = db.relationship("Supplier", back_populates="purchases")
