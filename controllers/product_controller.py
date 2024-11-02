from flask import request
from utils.db import connection_pool  

# Create product function
def create_product():
    data = request.get_json()
    if not data:
        return {'message': 'No input data provided'}, 400

    productname = data.get('productname')
    description = data.get('description')
    price = data.get('price')
    image_url = data.get('image_url')

    if not productname or not description or not price:
        return {'message': 'Product name, description, and price are required'}, 400

    if image_url and not isinstance(image_url, str):
        return {'message': 'Image URL must be a string'}, 400

    try:
        with connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO products (productname, description, price, image_url)
                    VALUES (%s, %s, %s, %s) RETURNING productid;
                """, (productname, description, price, image_url))
                product_id = cursor.fetchone()[0]
                conn.commit()

        return {'product_id': product_id, 'message': f'Product "{productname}" created successfully'}, 201
    except Exception as e:
        return {'message': 'Internal Server Error'}, 500

# Get all products function
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
                    'image_url': product[4],
                })
            return result, 200
        else:
            return {'message': 'No products found'}, 404
    except Exception as e:
        print(f"Error in get_all_products: {e}")
        return {'message': 'Internal Server Error'}, 500


# Get product by ID function

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
                'image_url': product[4], 
            }, 200
        else:
            return {'message': 'Product not found'}, 404
    except Exception as e:
        return {'message': 'Internal Server Error'}, 500


