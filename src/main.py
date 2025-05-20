             
import os
import sys
import datetime                  
from datetime import timedelta                   

                      
                                         
RED = '\033[91m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RESET = '\033[0m'                   

banner = f"""
{CYAN}
  _______      ____      _______          
 |  __ \ \    / /\ \    / / ____|   /\    
 | |  | \ \  / /  \ \  / / |       /  \   
 | |  | |\ \/ /    \ \/ /| |      / /\ \  
 | |__| | \  /      \  / | |____ / ____ \ 
 |_____/   \/        \/   \_____/_/    \_\\
{RESET}
{YELLOW}   Damn Vulnerable Vibe Code Application{RESET}
{RED}==========================================={RESET}
"""
print(banner)
                          


                       
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, render_template, abort, session                                       
from flask_login import LoginManager                      

                                                
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

                   
from src.routes.auth import auth_bp
from src.routes.shop import shop_bp
from src.routes.admin import admin_bp
from src.routes.profile import profile_bp                                   

                                                       
app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'))

app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'                                   

                            
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)                                     

                                  
                                                
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(project_dir, 'dvvca.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

                                     
                                        
app.config['PROFILE_PICS_UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'profile_pics')
app.config['PRODUCT_IMAGE_UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'product_images')

db.init_app(app)

                       
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'                                                  

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

                                                                        
@app.before_request
def make_session_permanent():
    session.permanent = True

                                        
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.datetime.now().year}

                                                               
with app.app_context():
    db.create_all()
    if not os.path.exists(app.config['PROFILE_PICS_UPLOAD_FOLDER']):
        os.makedirs(app.config['PROFILE_PICS_UPLOAD_FOLDER'], exist_ok=True)
    if not os.path.exists(app.config['PRODUCT_IMAGE_UPLOAD_FOLDER']):
        os.makedirs(app.config['PRODUCT_IMAGE_UPLOAD_FOLDER'], exist_ok=True)

                     
app.register_blueprint(auth_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(profile_bp)                                 

                             

                        
@app.route('/profile_pics/<filename>')
def serve_profile_pic(filename):
    profile_pics_folder = app.config['PROFILE_PICS_UPLOAD_FOLDER']
    if '..' in filename or filename.startswith('/'):
         abort(404)
    try:
        return send_from_directory(profile_pics_folder, filename)
    except FileNotFoundError:
                                                                 
                                                                                                    
        abort(404)

                      
@app.route('/product_images/<filename>')
def serve_product_image(filename):
                                                           
                                                                                                                   
    product_images_folder = app.config['PRODUCT_IMAGE_UPLOAD_FOLDER']
                                                                                                    
                                                                                                    
                                                                                                          
                                                                                           
                                                                                                  
    if '..' in filename or filename.startswith('/'):
         abort(404)
    try:
        return send_from_directory(product_images_folder, filename)
    except FileNotFoundError:
        abort(404)

                                                                      
                                                                                                                   
                                                                                                  
                                   
                               
                                                         


                        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
