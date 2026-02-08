from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    profile = db.relationship("BusinessProfile", backref="user", uselist=False)
    services = db.relationship("Service", backref="owner", lazy="dynamic")
    orders_as_buyer = db.relationship(
        "Order",
        backref="buyer",
        lazy="dynamic",
        foreign_keys="Order.buyer_id",
    )
    orders_as_seller = db.relationship(
        "Order",
        backref="seller",
        lazy="dynamic",
        foreign_keys="Order.seller_id",
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class BusinessProfile(db.Model):
    __tablename__ = "business_profiles"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    website = db.Column(db.String(255))
    location = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    contact_email = db.Column(db.String(120))

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<BusinessProfile {self.company_name}>"


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    delivery_time = db.Column(db.Integer, nullable=False)  # in days
    tags = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    orders = db.relationship("Order", backref="service", lazy="dynamic")

    def __repr__(self):
        return f"<Service {self.title}>"


class Order(db.Model):
    __tablename__ = "orders"

    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_COMPLETED = "completed"
    STATUS_REJECTED = "rejected"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default=STATUS_PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    messages = db.relationship("Message", backref="order", lazy="dynamic")

    def __repr__(self):
        return f"<Order {self.id} - {self.status}>"


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    sender = db.relationship("User", backref="messages_sent", lazy=True)

    def __repr__(self):
        return f"<Message {self.id} on order {self.order_id}>"
