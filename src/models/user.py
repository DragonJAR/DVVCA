from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
import datetime
from flask_login import UserMixin
from flask import url_for

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), nullable=False, default="user")
    full_name = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)                                           
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

                   
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    browsing_history = relationship("BrowsingHistory", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def profile_pic_url(self):
        """
        Returns the URL to the user's profile picture.
        - If the user has uploaded a picture, serve it from /profile_pics/<filename>.
        - Otherwise, serve the default from the Flask static folder.
        """
        if self.profile_picture:
            return url_for("serve_profile_pic", filename=self.profile_picture)
        else:
            return url_for("static", filename="default_profile.png")
