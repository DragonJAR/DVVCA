from . import db
import datetime
from sqlalchemy.orm import relationship

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
                                                                                    
                                                       
    card_number_last4 = db.Column(db.String(4), nullable=True)                            
    order_items = db.relationship("OrderItem", back_populates="order", lazy=True)

                   
    user = relationship("User", back_populates="orders")

    def __repr__(self):
        return f'<Order {self.id} by User {self.user_id}>'

    @property
    def created_at(self):
        """
        Alias for order_date to keep compatibility with templates.
        """
        return self.order_date

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_date': self.order_date.isoformat(),
            'total_amount': self.total_amount,
            'shipping_address': self.shipping_address,
            'card_number_last4': self.card_number_last4,
            'items': [item.to_dict() for item in self.order_items]
        }
