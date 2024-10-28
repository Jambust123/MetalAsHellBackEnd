from flask import Flask
from flask_cors import CORS
from controllers.user_controller import create_user, get_users, get_user_by_username
from controllers.product_controller import create_product, get_all_products, get_product_by_id
from controllers.category_controller import get_categories
from utils.db import connection_pool
from models.category import Category
from models.product import Product

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

def initialize_database():
    """Create tables and seed initial data."""
    with connection_pool.getconn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(Category.create_table())
            cursor.execute(Category.seed_categories())
            cursor.execute(Product.create_table())
            conn.commit()

@app.route('/api/users', methods=['POST'])
def user_creation():
    return create_user()

@app.route('/api/users', methods=['GET'])
def list_users():
    return get_users()

@app.route('/api/users/<username>', methods=['GET'])
def user_details(username):
    return get_user_by_username(username)

@app.route('/api/products', methods=['POST'])
def product_creation():
    return create_product()

@app.route('/api/products', methods=['GET'])
def list_products():
    return get_all_products()

@app.route('/api/categories', methods=['GET'])
def categories_list():
    return get_categories()

@app.route('/api/products/<int:product_id>', methods=['GET'])
def product_details(product_id):
    return get_product_by_id(product_id)

if __name__ == '__main__':
    # Initialize the database when the application starts
    initialize_database()
    
    # Run the application
    app.run(host='0.0.0.0', port=4000)
