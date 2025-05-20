from . import db
import datetime
from sqlalchemy.orm import relationship

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)                     
    comment = db.Column(db.Text, nullable=True)
    review_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.id} for Product {self.product_id} by User {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'comment': self.comment,
            'review_date': self.review_date.isoformat()
        }



                   
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")

