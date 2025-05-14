from . import db
from sqlalchemy.orm import relationship

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    image_url = db.Column(db.String(255), nullable=True) # Filename for local image or external URL
    # Add specs field for electronics?
    specifications = db.Column(db.Text, nullable=True) # Simple text field for specs for now

    category = relationship("Category", back_populates="products")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product") # Don't cascade delete orders if product is deleted?

    # New Relationships for History and Favorites
    viewed_by_users = relationship("BrowsingHistory", back_populates="product", cascade="all, delete-orphan")
    favorited_by_users = relationship("Favorite", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
         return f"<Product {self.name}>"
