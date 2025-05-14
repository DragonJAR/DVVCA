from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from functools import wraps
from src.models import db
from src.models.user import User
from src.models.category import Category
from src.models.product import Product
import requests # For SSRF
import pickle # For Insecure Deserialization
import base64 # To handle pickled data transfer
from werkzeug.utils import secure_filename
import os

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin", url_prefix="/admin")

# Decorator to check if user is admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Admin privileges are required to access this page.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/")
@admin_required
def dashboard():
    user_count = User.query.count()
    product_count = Product.query.count()
    category_count = Category.query.count()
    return render_template("dashboard.html", user_count=user_count, product_count=product_count, category_count=category_count)

# --- Product Management ---
@admin_bp.route("/products")
@admin_required
def manage_products():
    products = Product.query.join(Category).options(db.joinedload(Product.category)).order_by(Product.name).all()
    return render_template("manage_products.html", products=products)

@admin_bp.route("/products/add", methods=["GET", "POST"])
@admin_required
def add_product():
    categories = Category.query.order_by(Category.name).all()
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        category_id = request.form.get("category_id")
        specifications = request.form.get("specifications")

        if not name or not price or not category_id:
            flash("Name, price, and category are required.", "danger")
            return render_template("add_edit_product.html", action="Add", categories=categories)

        try:
            price_float = float(price)
            category_obj = Category.query.get(category_id)
            if not category_obj:
                 flash("Invalid category.", "danger")
                 return render_template("add_edit_product.html", action="Add", categories=categories)

            image_url_for_db = None
            image_file = request.files.get("image")
            if image_file and image_file.filename != "":
                filename = secure_filename(image_file.filename)
                upload_folder = current_app.config.get("PRODUCT_IMAGE_UPLOAD_FOLDER", os.path.join(current_app.root_path, "static", "product_images"))
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder, exist_ok=True)
                image_file.save(os.path.join(upload_folder, filename))
                image_url_for_db = filename
            
            new_product = Product(
                name=name,
                description=description,
                price=price_float,
                category_id=int(category_id),
                image_url=image_url_for_db, 
                specifications=specifications
            )
            db.session.add(new_product)
            db.session.commit()
            flash("Product added successfully!", "success")
            return redirect(url_for("admin.manage_products"))
        except ValueError:
            flash("Invalid price format.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding product: {str(e)}", "danger")

    return render_template("add_edit_product.html", action="Add", categories=categories)

@admin_bp.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.order_by(Category.name).all()

    if request.method == "POST":
        product.name = request.form.get("name")
        product.description = request.form.get("description")
        product.price = float(request.form.get("price"))
        product.category_id = int(request.form.get("category_id"))
        product.specifications = request.form.get("specifications")

        image_file = request.files.get("image")
        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            upload_folder = current_app.config.get("PRODUCT_IMAGE_UPLOAD_FOLDER", os.path.join(current_app.root_path, "static", "product_images"))
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder, exist_ok=True)
            image_file.save(os.path.join(upload_folder, filename))
            product.image_url = filename

        if not product.name or not product.price or not product.category_id:
            flash("Name, price, and category are required.", "danger")
            return render_template("add_edit_product.html", action="Edit", product=product, categories=categories, product_id=product_id)

        try:
            db.session.commit()
            flash("Product updated successfully!", "success")
            return redirect(url_for("admin.manage_products"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating product: {str(e)}", "danger")

    return render_template("add_edit_product.html", action="Edit", product=product, categories=categories, product_id=product_id)

@admin_bp.route("/products/delete/<int:product_id>", methods=["POST"])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting product: {str(e)}. Ensure it's not in any orders or carts.", "danger")
    return redirect(url_for("admin.manage_products"))

# --- Category Management ---
@admin_bp.route("/categories", methods=["GET", "POST"])
@admin_required
def manage_categories():
    if request.method == "POST":
        category_name = request.form.get("category_name")
        if category_name:
            existing = Category.query.filter_by(name=category_name).first()
            if not existing:
                new_category = Category(name=category_name)
                db.session.add(new_category)
                try:
                    db.session.commit()
                    flash("Category added successfully.", "success")
                except Exception as e:
                    db.session.rollback()
                    flash(f"Error adding category: {str(e)}", "danger")
            else:
                flash("Category already exists.", "warning")
        else:
            flash("Category name cannot be empty.", "danger")
        return redirect(url_for("admin.manage_categories"))

    categories = Category.query.order_by(Category.name).all()
    return render_template("manage_categories.html", categories=categories)

@admin_bp.route("/categories/delete/<int:category_id>", methods=["POST"])
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.products:
        flash("Cannot delete category because it contains products.", "danger")
    else:
        try:
            db.session.delete(category)
            db.session.commit()
            flash("Category deleted successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting category: {str(e)}", "danger")
    return redirect(url_for("admin.manage_categories"))

# --- User Management ---
@admin_bp.route("/users")
@admin_required
def manage_users():
    users = User.query.order_by(User.username).all()
    return render_template("manage_users.html", users=users)

@admin_bp.route("/users/role/<int:user_id>", methods=["POST"])
@admin_required
def change_user_role(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot change your own role.", "danger")
        return redirect(url_for("admin.manage_users"))

    if user.role == "admin":
        user.role = "user"
        action_taken = "demoted to User"
    elif user.role == "user":
        user.role = "admin"
        action_taken = "promoted to Admin"
    else:
        # Should not happen with current roles, but good for robustness
        flash(f"User {user.username} has an unrecognized role: {user.role}", "danger")
        return redirect(url_for("admin.manage_users"))

    try:
        db.session.commit()
        flash(f"Role of {user.username} {action_taken}.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error changing role for {user.username}: {str(e)}", "danger")
    return redirect(url_for("admin.manage_users"))

@admin_bp.route("/users/delete/<int:user_id>", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("admin.manage_users"))

    try:
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.username} deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {str(e)}. Ensure they have no orders, etc.", "danger")
    return redirect(url_for("admin.manage_users"))

# --- Vulnerability: SSRF --- 
@admin_bp.route("/fetch_url", methods=["GET", "POST"])
@admin_required
def fetch_url_data():
    content = None
    url = ""
    if request.method == "POST":
        url = request.form.get("url_to_fetch")
        if url:
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                content = response.text
                flash(f"Content fetched from {url}", "success")
            except requests.exceptions.RequestException as e:
                flash(f"Error fetching URL {url}: {str(e)}", "danger")
                content = f"Error: {str(e)}"
        else:
            flash("Please enter a URL.", "warning")
    return render_template("fetch_url.html", fetched_content=content, requested_url=url)
# --- End SSRF --- 

# --- Vulnerability: Insecure Deserialization --- 
@admin_bp.route("/import_data", methods=["GET", "POST"])
@admin_required
def import_data():
    result = None
    if request.method == "POST":
        pickled_data_b64 = request.form.get("pickled_data")
        if pickled_data_b64:
            try:
                pickled_data = base64.b64decode(pickled_data_b64)
                deserialized_object = pickle.loads(pickled_data)
                result = f"Data deserialized successfully: {deserialized_object}"
                flash("Data imported (deserialized).", "success")
            except base64.binascii.Error:
                flash("Error: Input is not valid Base64.", "danger")
            except pickle.UnpicklingError:
                flash("Error: Could not deserialize (invalid pickle).", "danger")
            except Exception as e:
                flash(f"Error during deserialization: {str(e)}", "danger")
        else:
            flash("Please provide Base64 encoded serialized data.", "warning")
    return render_template("import_data.html", result=result)
# --- End Insecure Deserialization --- 

# --- Vulnerability: Broken Access Control --- 
@admin_bp.route("/system_info")
# INTENTIONALLY MISSING: @admin_required or @login_required
def system_info():
    return render_template("admin/system_info.html")
# --- End Broken Access Control --- 

