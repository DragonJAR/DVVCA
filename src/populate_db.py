import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from werkzeug.security import generate_password_hash

from src.main import app, db
from src.models.category import Category
from src.models.product import Product
from src.models.user import User

# Path to the JSON file with product data
PRODUCTS_JSON_PATH = "../parsed_products.json"
STATIC_IMAGES_PATH = "./static/product_images"

# Sample user data
sample_users = [
    {"username": "admin", "email": "admin@dvvca.test", "password": "password", "role": "admin"},
    {"username": "admin2", "email": "admin2@dvvca.test", "password": "admin123", "role": "admin"},
    {"username": "user1", "email": "user1@dvvca.test", "password": "password123", "role": "user"},
    {"username": "user2", "email": "user2@dvvca.test", "password": "123456", "role": "user"},
    {"username": "testuser", "email": "test@example.com", "password": "password123", "role": "user"}
]

def load_products_from_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
        return products
    except FileNotFoundError:
        print(f"Error: Product data file not found at {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")
        return []

def populate():
    products_data = load_products_from_json(PRODUCTS_JSON_PATH)
    if not products_data:
        print("No product data loaded. Aborting database population.")
        return

    with app.app_context():
        print("Dropping existing tables...")
        db.drop_all()
        print("Creating new tables...")
        db.create_all()
        print("Populating database...")
        
        # Populate Categories and Products
        for data in products_data:
            category_name = data.get("category_name", "Uncategorized")
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                print(f'Creating category: {category_name}') 
                category = Category(name=category_name)
                db.session.add(category)
                db.session.flush() # Flush to get category.id
            
            existing_product = Product.query.filter_by(name=data["name"]).first()
            if not existing_product:
                image_path_from_json = data.get("image_url", "product_images/default.png")
                image_filename_base = os.path.splitext(os.path.basename(image_path_from_json))[0]
                
                image_filename_to_save = "default.png" # Default value

                if image_filename_base == "default":
                    image_filename_to_save = "default.png"
                else:
                    # Attempt to use .jpeg first as downloaded images are mostly .jpeg
                    potential_image_name_jpeg = image_filename_base + ".jpeg"
                    if os.path.exists(os.path.join(STATIC_IMAGES_PATH, potential_image_name_jpeg)):
                        image_filename_to_save = potential_image_name_jpeg
                    else:
                        # If .jpeg not found, try .png (original from JSON)
                        potential_image_name_png = image_filename_base + ".png"
                        if os.path.exists(os.path.join(STATIC_IMAGES_PATH, potential_image_name_png)):
                            image_filename_to_save = potential_image_name_png
                        else:
                            print(f"Warning: Image for product '{data['name']}' ({potential_image_name_jpeg} or {potential_image_name_png}) not found in {STATIC_IMAGES_PATH}. Falling back to default.png.")
                            image_filename_to_save = "default.png"

                print(f'Adding product: {data["name"]} with image: {image_filename_to_save}') 
                product = Product(
                    name=data["name"],
                    description=data.get("description", "No description available."),
                    specifications=data.get("specifications", "N/A"),
                    price=float(data.get("price", 0.0)),
                    category_id=category.id,
                    image_url=image_filename_to_save
                )
                db.session.add(product)
            else:
                print(f'Product already exists: {data["name"]}')

        # Populate Sample Users
        print("Adding sample users...")
        for user_data in sample_users:
            existing_user = User.query.filter_by(username=user_data["username"]).first()
            if not existing_user:
                print(f'Adding user: {user_data["username"]}')
                hashed_password = generate_password_hash(user_data["password"], method="pbkdf2:sha256")
                new_user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    password_hash=hashed_password,
                    role=user_data["role"]
                )
                db.session.add(new_user)
            else:
                print(f'User already exists: {user_data["username"]}')

        try:
            db.session.commit()
            print("Database populated successfully with products and users!")
        except Exception as e:
            db.session.rollback()
            print(f"Error populating database: {e}")

if __name__ == "__main__":
    populate()

