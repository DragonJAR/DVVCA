from . import db
import datetime
from sqlalchemy.orm import relationship

class BrowsingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    user = relationship("User", back_populates="browsing_history")
    product = relationship("Product", back_populates="viewed_by_users")                                               

                                                                             
                                                                      
                                                                                  

    def __repr__(self):
        return f"<BrowsingHistory User:{self.user_id} Product:{self.product_id}>"
