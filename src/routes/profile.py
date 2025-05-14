from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from src.models import db
from src.models.user import User
from src.models.browsing_history import BrowsingHistory
from src.models.favorite import Favorite
from src.models.product import Product
from werkzeug.utils import secure_filename
import os

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route("/")
@login_required
def view_profile():
    recent_history = (
        BrowsingHistory.query
        .filter_by(user_id=current_user.id)
        .order_by(BrowsingHistory.viewed_at.desc())
        .limit(5)
        .all()
    )
    recent_favorites = (
        Favorite.query
        .filter_by(user_id=current_user.id)
        .order_by(Favorite.added_at.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "profile/view.html",
        user=current_user,
        recent_history=recent_history,
        recent_favorites=recent_favorites
    )

@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    user = User.query.get_or_404(current_user.id)

    if request.method == "POST":
        # --- Mass Assignment Protection: only update allowed fields ---
        allowed_fields = {"full_name", "bio"}
        for key, value in request.form.items():
            if key in allowed_fields:
                setattr(user, key, value)

        # --- Handle profile picture upload ---
        profile_pic = request.files.get("profile_pic")
        if profile_pic and profile_pic.filename:
            filename = secure_filename(profile_pic.filename)
            if allowed_file(filename):
                # Use the same upload folder configured in app.py
                upload_folder = current_app.config["PROFILE_PICS_UPLOAD_FOLDER"]
                os.makedirs(upload_folder, exist_ok=True)

                _, ext = os.path.splitext(filename)
                new_filename = f"user_{user.id}{ext}"
                save_path = os.path.join(upload_folder, new_filename)

                try:
                    profile_pic.save(save_path)
                    # Save the filename in the model, not the URL
                    user.profile_picture = new_filename
                    flash("Profile picture uploaded successfully!", "success")
                except Exception as e:
                    flash(f"Error saving profile picture: {e}", "danger")
            else:
                flash(
                    f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
                    "warning"
                )

        try:
            db.session.commit()
            flash("Profile updated successfully.", "success")
            return redirect(url_for("profile.view_profile"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {e}", "danger")

    return render_template("profile/edit.html", user=user)

@profile_bp.route("/history")
@login_required
def view_history():
    history = (
        BrowsingHistory.query
        .filter_by(user_id=current_user.id)
        .join(Product, BrowsingHistory.product_id == Product.id)
        .add_columns(Product.name, Product.price, BrowsingHistory.viewed_at)
        .order_by(BrowsingHistory.viewed_at.desc())
        .all()
    )
    history_data = [
        {
            "product_id": h.BrowsingHistory.product_id,
            "name": h.name,
            "price": h.price,
            "viewed_at": h.viewed_at
        }
        for h in history
    ]
    return render_template("profile/history.html", history=history_data)

@profile_bp.route("/favorites")
@login_required
def view_favorites():
    favorites = (
        Favorite.query
        .filter_by(user_id=current_user.id)
        .join(Product, Favorite.product_id == Product.id)
        .add_columns(Product.id, Product.name, Product.price, Product.image_url)
        .order_by(Favorite.added_at.desc())
        .all()
    )
    favorites_data = [
        {
            "product_id": f.id,
            "name": f.name,
            "price": f.price,
            "image": f.image_url
        }
        for f in favorites
    ]
    return render_template("profile/favorites.html", favorites=favorites_data)
