from . import db
from sqlalchemy.orm import relationship

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)                                   

    def __repr__(self):
        return f'<OrderItem order={self.order_id} product={self.product_id} qty={self.quantity}>'

    @property
    def subtotal(self):
        """
        Returns the subtotal for this order item: quantity * price at purchase.
        """
        return self.quantity * self.price_at_purchase

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price_at_purchase': self.price_at_purchase,
            'subtotal': self.subtotal
        }

                   
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")