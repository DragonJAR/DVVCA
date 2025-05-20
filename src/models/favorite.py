from . import db
import datetime
from sqlalchemy.orm import relationship

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="favorites")
    product = relationship("Product", back_populates="favorited_by_users")                                                  

                                                                          
    db.UniqueConstraint("user_id", "product_id", name="uq_user_product_favorite")

    def __repr__(self):
        return f"<Favorite User:{self.user_id} Product:{self.product_id}>"
