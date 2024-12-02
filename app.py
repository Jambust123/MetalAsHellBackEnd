from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from controllers.user_controller import create_user, get_users, get_user_by_username
from controllers.product_controller import create_product, get_all_products, get_product_by_id, get_products_by_category
from controllers.category_controller import get_categories
from utils.db import connection_pool
from models.category import Category
from models.product import Product
from models.user import User
import stripe
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

UPLOAD_FOLDER = 'uploads/images' 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size (16 MB)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def initialize_database():
    """Create tables and seed initial data."""
    with connection_pool.getconn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(Category.create_table())
            cursor.execute(Category.seed_categories())
            cursor.execute(Product.create_table())
            cursor.execute(User.create_table())
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

@app.route('/api/products/category/<int:category_id>', methods=['GET'])
def products_by_category(category_id):
    return get_products_by_category(category_id)

@app.route('/api/products/<int:product_id>', methods=['GET'])
def product_details(product_id):
    return get_product_by_id(product_id)

@app.route('/api/categories', methods=['GET'])
def categories_list():
    return get_categories()

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/create-payment-intent', methods=['POST'])
def create_payment_intent():
    """
    Creates a Stripe PaymentIntent for the specified amount.
    """
    try:
        data = request.json
        amount = int(data['amount'])  # Amount in cents (e.g., $10.00 -> 1000)
        email = data.get('email', None)

        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            receipt_email=email,
        )
        return jsonify({"clientSecret": payment_intent.client_secret})
    except Exception as e:
        print(f"Error creating PaymentIntent: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    initialize_database()
    app.run(host='0.0.0.0', port=4000)
