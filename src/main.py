import os
import sys
import datetime # Add this import
from datetime import timedelta # Import timedelta
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, render_template, abort, session # Import session for SESSION_PERMANENT
from flask_login import LoginManager # Import LoginManager

# Import all models to ensure tables are created
from src.models import db
from src.models.user import User
from src.models.category import Category
from src.models.product import Product
from src.models.cart_item import CartItem
from src.models.order import Order
from src.models.order_item import OrderItem
from src.models.review import Review
# Import new models
from src.models.browsing_history import BrowsingHistory
from src.models.favorite import Favorite

# Import Blueprints
from src.routes.auth import auth_bp
from src.routes.shop import shop_bp
from src.routes.admin import admin_bp
from src.routes.profile import profile_bp # Import the new profile blueprint

# Initialize Flask App with template and static folders
app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'))

app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT' # Keep the default or change later

# Configure Session Lifetime
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1) # Set session lifetime (e.g., 1 day)

# Configure Database to use SQLite
# Get the absolute path of the project directory
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(project_dir, 'dvvca.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Define upload folder configurations
# Ahora guardamos todo dentro de static/
app.config['PROFILE_PICS_UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'profile_pics')
app.config['PRODUCT_IMAGE_UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'product_images')

db.init_app(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login' # Redirect to login page if user is not logged in

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Make session permanent before each request if user chose 'remember me'
@app.before_request
def make_session_permanent():
    session.permanent = True

# Add context processor for current year
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.datetime.now().year}

# Create database tables and upload folders if they don't exist
with app.app_context():
    db.create_all()
    if not os.path.exists(app.config['PROFILE_PICS_UPLOAD_FOLDER']):
        os.makedirs(app.config['PROFILE_PICS_UPLOAD_FOLDER'], exist_ok=True)
    if not os.path.exists(app.config['PRODUCT_IMAGE_UPLOAD_FOLDER']):
        os.makedirs(app.config['PRODUCT_IMAGE_UPLOAD_FOLDER'], exist_ok=True)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(profile_bp) # Register the profile blueprint

# --- Static File Serving ---

# Serve profile pictures
@app.route('/profile_pics/<filename>')
def serve_profile_pic(filename):
    profile_pics_folder = app.config['PROFILE_PICS_UPLOAD_FOLDER']
    if '..' in filename or filename.startswith('/'):
         abort(404)
    try:
        return send_from_directory(profile_pics_folder, filename)
    except FileNotFoundError:
        # Try to serve a default if actual not found, or just 404
        # For now, let's assume default is handled by template logic if user.profile_pic_url is None
        abort(404)

# Serve product images
@app.route('/product_images/<filename>')
def serve_product_image(filename):
    # Product images are saved in src/static/product_images
    # So, the send_from_directory should point there relative to app.static_folder or use absolute path from config
    product_images_folder = app.config['PRODUCT_IMAGE_UPLOAD_FOLDER'] 
    # The app.static_folder is 'src/static'. So product_images_folder is 'src/static/product_images'
    # send_from_directory for static files is usually relative to app.static_folder if not absolute.
    # However, since PRODUCT_IMAGE_UPLOAD_FOLDER is already an absolute path to src/static/product_images,
    # we can use it directly. Or, more Flask-like, serve it as part of the static endpoint.
    # For consistency with how it's saved and to simplify, let's use the configured absolute path.
    if '..' in filename or filename.startswith('/'):
         abort(404)
    try:
        return send_from_directory(product_images_folder, filename)
    except FileNotFoundError:
        abort(404)

# Serve general static files (CSS, JS, default images from src/static)
# This route is usually handled by Flask automatically if static_folder is set and files are in /static/<path:path>
# Explicitly defining it can be for specific needs or if auto-handling is not working as expected.
# @app.route('/static/<path:path>')
# def serve_static_files(path):
#     return send_from_directory(app.static_folder, path)


# --- Main Execution ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

