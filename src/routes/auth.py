from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, current_user
from src.models import db
from src.models.user import User
from sqlalchemy import text                          

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("shop.index"))
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not email or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or email already exists.", "warning")
            return render_template("register.html")

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error during registration: {str(e)}", "danger")
            return render_template("register.html")

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("shop.index"))
        
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("login.html")

                                                                                     
                                                                                       
        user_for_auth = None
        try:
                                                                                   
            sql_query = f"SELECT id, username, password_hash, role FROM user WHERE username = \'{username}\'"
            result = db.session.execute(text(sql_query))
            user_data_from_sqli = result.fetchone()
            if user_data_from_sqli:
                                                                                         
                                                                                        
                                                                                               
                                                                          
                user_for_auth = User.query.get(user_data_from_sqli[0])                              
        except Exception:
                                                                                                 
            pass                             

        if not user_for_auth:                                                    
            user_for_auth = User.query.filter_by(username=username).first()

        if user_for_auth:
                                                                                               
            if user_for_auth.check_password(password):
                login_user(user_for_auth, remember=remember)
                flash("Login successful!", "success")
                next_page = request.args.get("next")
                if user_for_auth.role == "admin":
                    return redirect(next_page or url_for("admin.dashboard"))
                else:
                    return redirect(next_page or url_for("shop.index"))
            else:
                flash("Invalid password.", "danger")                     
        else:
            flash("User does not exist.", "danger")                 

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

