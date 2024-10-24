import os
from psycopg2 import pool
from dotenv import load_dotenv
from flask import Flask, request
import logging
from werkzeug.security import generate_password_hash
from flask_cors import CORS

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Connection Pool
connection_pool = pool.SimpleConnectionPool(1, 20, dsn=DATABASE_URL)

# Function to create tables if they don't exist
def create_tables():
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        userid SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
    );
    """

    create_products_table = """
    CREATE TABLE IF NOT EXISTS products (
        productid SERIAL PRIMARY KEY,
        productname VARCHAR(100) NOT NULL,
        description TEXT NOT NULL,
        price DECIMAL(10, 2) NOT NULL
    );
    """

    try:
        with connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_users_table)
                cursor.execute(create_products_table)
                conn.commit()
                logger.info("Tables created successfully (if they didn't exist).")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")

# Create the tables on startup
create_tables()

@app.route('/')
def index():
    return {'message': 'Welcome to the Metal As Hell API Home'}

@app.get('/api')
def welcome_message():
    return {'message': 'Welcome to the Metal As Hell API'}

@app.post('/api/users')
def create_user():
    try:
        data = request.get_json()
        if not data:
            return {'message': 'No input data provided'}, 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return {'message': 'Username, email, and password are required'}, 400

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Get a connection from the pool
        conn = connection_pool.getconn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s;", (username,))
            if cursor.fetchone()[0] > 0:
                return {'message': 'Username already exists'}, 400
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s;", (email,))
            if cursor.fetchone()[0] > 0:
                return {'message': 'Email already exists'}, 400

            cursor.execute("""
                INSERT INTO users (username, email, password)
                VALUES (%s, %s, %s) RETURNING userid;
            """, (username, email, hashed_password))
            user_id = cursor.fetchone()[0]

            conn.commit()

        logger.info(f"User '{username}' created with ID {user_id}")
        return {'user_id': user_id, 'message': f'User "{username}" created successfully'}, 201

    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return {'message': f'Internal Server Error: {str(e)}'}, 500
    finally:
        if conn:
            connection_pool.putconn(conn)

@app.get('/api/users')
def get_users():
    try:
        conn = connection_pool.getconn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT userid, username, email FROM users;")
            users = cursor.fetchall()

        if users:
            user_list = []
            for user in users:
                user_list.append({
                    'user_id': user[0],
                    'username': user[1],
                    'email': user[2]
                })
            return {'users': user_list}, 200
        else:
            return {'message': 'No users found'}, 404
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        return {'message': 'Internal Server Error'}, 500
    finally:
        if conn:
            connection_pool.putconn(conn)

@app.get('/api/users/<username>')
def get_user_by_username(username):
    try:
        conn = connection_pool.getconn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT userid, username, email FROM users WHERE username = %s;", (username,))
            user = cursor.fetchone()

        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'email': user[2]
            }, 200
        else:
            return {'message': 'User not found'}, 404
    except Exception as e:
        logger.error(f"Error retrieving user: {e}")
        return {'message': 'Internal Server Error'}, 500
    finally:
        if conn:
            connection_pool.putconn(conn)

# Define Create Product Endpoint
@app.post('/api/products')
def create_product():
    try:
        data = request.get_json()
        if not data:
            return {'message': 'No input data provided'}, 400

        productname = data.get('productname')
        description = data.get('description')
        price = data.get('price')

        if not productname or not description or not price:
            return {'message': 'Product name, description, and price are required'}, 400

        conn = connection_pool.getconn()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO products (productname, description, price)
                VALUES (%s, %s, %s) RETURNING productid;
            """, (productname, description, price))
            product_id = cursor.fetchone()[0]
            conn.commit()

        return {'product_id': product_id, 'message': f'Product "{productname}" created successfully'}, 201
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        return {'message': 'Internal Server Error'}, 500
    finally:
        if conn:
            connection_pool.putconn(conn)

# Define Get Product Endpoint
@app.get('/api/products/<int:product_id>')
def get_product(product_id):
    try:
        conn = connection_pool.getconn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE productid = %s;", (product_id,))
            product = cursor.fetchone()

        if product:
            return {
                'product_id': product[0],
                'productname': product[1],
                'description': product[2],
                'price': float(product[3])
            }, 200
        else:
            return {'message': 'Product not found'}, 404
    except Exception as e:
        logger.error(f"Error retrieving product: {e}")
        return {'message': 'Internal Server Error'}, 500
    finally:
        if conn:
            connection_pool.putconn(conn)

# Define Get All Products Endpoint
@app.get('/api/products')
def get_all_products():
    try:
        conn = connection_pool.getconn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM products;")
            products = cursor.fetchall()

        if products:
            result = []
            for product in products:
                result.append({
                    'product_id': product[0],
                    'productname': product[1],
                    'description': product[2],
                    'price': float(product[3])
                })

            return result, 200
        else:
            return {'message': 'No products found'}, 404
    except Exception as e:
        logger.error(f"Error retrieving products: {e}")
        return {'message': 'Internal Server Error'}, 500
    finally:
        if conn:
            connection_pool.putconn(conn)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 4000))
    app.run(host='0.0.0.0', port=port)
