import os
from werkzeug.utils import secure_filename
from flask import request
from utils.db import connection_pool 
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'uploads/images'

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create product function
def create_product():
    data = request.form  # For text fields
    productname = data.get('productname')
    description = data.get('description')
    price = data.get('price')
    category_id = data.get('category_id')

    if not productname or not description or not price:
        return {'message': 'Product name, description, and price are required'}, 400

    file = request.files.get('image')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        image_url = f'/uploads/{filename}'
    else:
        file_path = None

    try:
        with connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO products (productname, description, price, categoryid, image_url)
                    VALUES (%s, %s, %s, %s, %s) RETURNING productid;
                """, (productname, description, price, category_id, file_path, image_url))
                product_id = cursor.fetchone()[0]
                conn.commit()

        return {'product_id': product_id, 'message': f'Product "{productname}" created successfully'}, 201
    except Exception as e:
        print(f"Error creating product: {e}")
        return {'message': 'Internal Server Error'}, 500



def get_all_products():
    try:
        with connection_pool.getconn() as conn:
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
                    'price': float(product[3]),
                    'category_id': product[4],
                    'image_url': product[5],
                })
            return result, 200
        else:
            return {'message': 'No products found'}, 404
    except Exception as e:
        print(f"Error in get_all_products: {e}")
        return {'message': 'Internal Server Error'}, 500


def get_product_by_id(product_id):
    try:
        with connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM products WHERE productid = %s;", (product_id,))
                product = cursor.fetchone()

        if product:
            return {
                'product_id': product[0],
                'productname': product[1],
                'description': product[2],
                'price': float(product[3]),
                'category_id': product[4],
                'image_url': product[5],
            }, 200
        else:
            return {'message': 'Product not found'}, 404
    except Exception as e:
        return {'message': 'Internal Server Error'}, 500

def get_products_by_category(category_id):
    try:
        with connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM products WHERE categoryid = %s;", (category_id,))
                products = cursor.fetchall()

        if products:
            result = []
            for product in products:
                result.append({
                    'product_id': product[0],
                    'productname': product[1],
                    'description': product[2],
                    'price': float(product[3]),
                    'category_id': product[4],
                    'image_url': product[5],
                })
            return result, 200
        else:
            return {'message': 'No products found for this category'}, 404
    except Exception as e:
        print(f"Error in get_products_by_category: {e}")
        return {'message': 'Internal Server Error'}, 500

