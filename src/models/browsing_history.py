from . import db
import datetime
from sqlalchemy.orm import relationship

class BrowsingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    user = relationship("User", back_populates="browsing_history")
    product = relationship("Product", back_populates="viewed_by_users") # Need to add viewed_by_users to Product model

    # Unique constraint to avoid multiple entries for the same user/product? 
    # Or just update timestamp? Let's update timestamp for simplicity.
    # db.UniqueConstraint("user_id", "product_id", name="uq_user_product_history")

    def __repr__(self):
        return f"<BrowsingHistory User:{self.user_id} Product:{self.product_id}>"
