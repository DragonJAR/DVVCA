from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_login import login_required, current_user                                      
import os                               
from src.models import db
from src.models.user import User
from src.models.category import Category
from src.models.product import Product
from src.models.cart_item import CartItem
from src.models.order import Order
from src.models.order_item import OrderItem
from src.models.review import Review
from src.models.browsing_history import BrowsingHistory                         
from src.models.favorite import Favorite                  
import datetime

shop_bp = Blueprint("shop", __name__, template_folder="../templates/shop")

                                                                   
IMAGE_DIR = "/home/ubuntu/dvvca/product_images"

@shop_bp.route("/")
def index():
                                              
    try:
        categories = Category.query.order_by(Category.name).all()
                                                   
        products = Product.query.order_by(Product.id.desc()).limit(6).all()
    except Exception as e:
                                            
        flash(f"Error loading main page: {e}", "danger")
        categories = []
        products = []
    return render_template("index.html", categories=categories, products=products)

@shop_bp.route("/category/<int:category_id>")
def view_category(category_id):
                                     
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category.id).order_by(Product.name).all()
    return render_template("category.html", category=category, products=products)

@shop_bp.route("/product/<int:product_id>")
def view_product(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product.id).order_by(Review.review_date.desc()).all()
    avg_rating = db.session.query(db.func.avg(Review.rating)).filter(Review.product_id == product.id).scalar() or 0

                                   
    if current_user.is_authenticated:
        try:
                                                                                    
                                                          
            history_entry = BrowsingHistory(user_id=current_user.id, product_id=product.id, viewed_at=datetime.datetime.utcnow())
            db.session.add(history_entry)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
                                                                                
            print(f"Error logging browsing history: {e}")
                                   

                                                       
    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = Favorite.query.filter_by(user_id=current_user.id, product_id=product.id).first() is not None

    return render_template("product.html", product=product, reviews=reviews, avg_rating=avg_rating, is_favorite=is_favorite)

                                        
                                                                               
                                                                                      
                                  
                          
         
                             

@shop_bp.route("/search")
def search_products():
    query = request.args.get("q", "")
    results = []
    if query:
                                                                                     
                                                                              
        flash(f"Showing results for: {query}", "info")                          
                                                 
        results = Product.query.filter(Product.name.contains(query)).all()               

    return render_template("search_results.html", query=query, results=results)

                      
@shop_bp.route("/cart")
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).join(Product).options(db.joinedload(CartItem.product)).all()
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    return render_template("cart.html", cart_items=cart_items, total_price=total_price)

@shop_bp.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get("quantity", 1))

    if quantity < 1:
        flash("Quantity must be at least 1.", "warning")
        return redirect(request.referrer or url_for("shop.view_product", product_id=product_id))

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    try:
        db.session.commit()
        flash(f"'{product.name}' added to cart!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding to cart: {e}", "danger")

                                    
    return redirect(request.referrer or url_for("shop.index"))

@shop_bp.route("/cart/update/<int:item_id>", methods=["POST"])
@login_required
def update_cart_item(item_id):
                                    
    cart_item = CartItem.query.get_or_404(item_id)
                                                                                                
    if cart_item.user_id != current_user.id:                                                       
         abort(403)

    quantity = int(request.form.get("quantity", 1))
    if quantity < 1:
        flash("Quantity must be at least 1.", "warning")
    else:
        cart_item.quantity = quantity
        try:
            db.session.commit()
            flash("Cart updated.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating cart: {e}", "danger")

                                    
    return redirect(url_for("shop.view_cart"))

@shop_bp.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_cart_item(item_id):
                                    
    cart_item = CartItem.query.get_or_404(item_id)
                                                                                                
    if cart_item.user_id != current_user.id:                    
         abort(403)

    try:
        db.session.delete(cart_item)
        db.session.commit()
        flash("Item removed from cart.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error removing from cart: {e}", "danger")

                                    
    return redirect(url_for("shop.view_cart"))

                                    
@shop_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).join(Product).options(db.joinedload(CartItem.product)).all()
    if not cart_items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("shop.index"))

    total_price = sum(item.quantity * item.product.price for item in cart_items)

    if request.method == "POST":
                                                                                             
        full_name = request.form.get("full_name")
        address = request.form.get("address")
        city = request.form.get("city")
        state = request.form.get("state")
        zip_code = request.form.get("zip_code")
        card_number = request.form.get("card_number")

        if not all([full_name, address, city, state, zip_code, card_number]):
            flash("Please fill in all fields.", "danger")
            return render_template("checkout.html", cart_items=cart_items, total_price=total_price)

        try:
            new_order = Order(
                user_id=current_user.id,
                total_amount=total_price,
                shipping_address=f"{full_name}\n{address}\n{city}, {state} {zip_code}",                       
                card_number_last4=card_number[-4:]                   
            )
            db.session.add(new_order)
            db.session.flush()

            for item in cart_items:
                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price_at_purchase=item.product.price
                )
                db.session.add(order_item)

            CartItem.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()
            flash("Order placed successfully!", "success")
            return redirect(url_for("shop.order_confirmation", order_id=new_order.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error processing order: {e}", "danger")
            return render_template("checkout.html", cart_items=cart_items, total_price=total_price)

    return render_template("checkout.html", cart_items=cart_items, total_price=total_price)

@shop_bp.route("/order_confirmation/<int:order_id>")
@login_required
def order_confirmation(order_id):
                                    
    order = Order.query.get_or_404(order_id)
                                                                                              
    if order.user_id != current_user.id:                    
        abort(403)

                                                                      
    return render_template("order_confirmation.html", order=order)

                       
@shop_bp.route("/product/<int:product_id>/review", methods=["POST"])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    rating = request.form.get("rating")
    comment = request.form.get("comment")                       

    if not rating:
        flash("Rating is required.", "danger")
        return redirect(url_for("shop.view_product", product_id=product_id))

    try:
        rating = int(rating)
        if not 1 <= rating <= 5:
            raise ValueError("Rating out of range")
    except ValueError:
        flash("Invalid rating.", "danger")
        return redirect(url_for("shop.view_product", product_id=product_id))

                                                                     
    new_review = Review(product_id=product_id, user_id=current_user.id, rating=rating, comment=comment)

    try:
        db.session.add(new_review)
        db.session.commit()
        flash("Review submitted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error submitting review: {e}", "danger")

                                    
    return redirect(url_for("shop.view_product", product_id=product_id))

                          
@shop_bp.route("/favorite/add/<int:product_id>", methods=["POST"])
@login_required
def add_favorite(product_id):
    product = Product.query.get_or_404(product_id)
    existing_favorite = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if not existing_favorite:
        new_favorite = Favorite(user_id=current_user.id, product_id=product_id)
        db.session.add(new_favorite)
        try:
            db.session.commit()
            flash(f"'{product.name}' added to favorites.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding to favorites: {e}", "danger")
    else:
        flash(f"'{product.name}' is already in your favorites.", "info")

                                    
    return redirect(request.referrer or url_for("shop.view_product", product_id=product_id))

@shop_bp.route("/favorite/remove/<int:product_id>", methods=["POST"])
@login_required
def remove_favorite(product_id):
                                                                                                        
    favorite = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first()
                                                                                                                              
                                                                                           

    if favorite:
        try:
            db.session.delete(favorite)
            db.session.commit()
            flash("Removed from favorites.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error removing from favorites: {e}", "danger")
    else:
        flash("This product is not in your favorites.", "warning")

                                    
    return redirect(request.referrer or url_for("profile.view_favorites"))                                         




@shop_bp.route("/products")
def view_all_products():
                        
    try:
        products = Product.query.order_by(Product.name).all()
    except Exception as e:
        flash(f"Error loading products: {e}", "danger")
        products = []
    return render_template("products.html", products=products)

