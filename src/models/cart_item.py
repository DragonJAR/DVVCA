from . import db
from sqlalchemy.orm import relationship

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return f'<CartItem user={self.user_id} product={self.product_id} qty={self.quantity}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity
        }

                   
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

    @property
    def subtotal(self):
        """
        Returns the subtotal for this cart item (quantity * unit price).
        """
                                         
        return self.quantity * self.product.price
