import unittest
from flask import json
from app import app  # Ensure this is your Flask app
from utils.db import connection_pool

class APITestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and test database."""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        self.app.config['DEBUG'] = False

        # Initialize database with a test connection pool if needed
        with connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("BEGIN;")  # Start a transaction for tests

    def tearDown(self):
        """Roll back any database changes after each test."""
        with connection_pool.getconn() as conn:
            conn.rollback()  # Roll back all test changes

    # ---- User Tests ----
    def test_create_user(self):
        response = self.client.post('/api/users', json={
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('user_id', data)

    def test_get_users(self):
        response = self.client.get('/api/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_get_user_by_username(self):
        username = 'testuser'
        self.client.post('/api/users', json={'username': username, 'password': 'testpassword'})
        response = self.client.get(f'/api/users/{username}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['username'], username)

    # ---- Product Tests ----
    def test_create_product(self):
        response = self.client.post('/api/products', json={
            'productname': 'Test Product',
            'description': 'A test product',
            'price': 19.99,
            'image_url': 'http://example.com/image.jpg'
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('product_id', data)

    def test_get_all_products(self):
        response = self.client.get('/api/products')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_get_product_by_id(self):
        # First, create a product
        create_response = self.client.post('/api/products', json={
            'productname': 'Test Product',
            'description': 'A test product',
            'price': 19.99,
            'image_url': 'http://example.com/image.jpg'
        })
        product_id = json.loads(create_response.data)['product_id']

        # Then, retrieve it by ID
        response = self.client.get(f'/api/products/{product_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['productname'], 'Test Product')

    # ---- Category Tests ----
    def test_get_categories(self):
        response = self.client.get('/api/categories')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)  # Check there's at least one category

    # ---- Additional Edge Case Tests ----
    def test_get_nonexistent_product(self):
        response = self.client.get('/api/products/9999')  # Assume ID 9999 doesn't exist
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Product not found')

    def test_create_product_invalid_data(self):
        response = self.client.post('/api/products', json={
            'productname': '',  # Missing name
            'description': 'Description only'
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Product name, description, and price are required')

if __name__ == '__main__':
    unittest.main()
