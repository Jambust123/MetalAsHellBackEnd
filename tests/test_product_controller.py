import os
import io
import pytest
from flask import Flask
from werkzeug.datastructures import FileStorage
from controllers.product_controller import create_product

# Create a Flask application for testing
app = Flask(__name__)

# Configure the app for testing
app.config['TESTING'] = True
app.config['UPLOAD_FOLDER'] = 'uploads/images'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_create_product_success(client):
    # Create a sample image file
    data = {
        'productname': 'Test Product',
        'description': 'This is a test product',
        'price': '19.99',
        'category_id': '1'
    }
    image_data = (io.BytesIO(b"fake image data"), 'test.jpg')
    
    # Send a POST request to the create_product endpoint
    response = client.post('/api/products', data={
        **data,
        'image': image_data
    }, content_type='multipart/form-data')

    # Assert the response
    assert response.status_code == 201
    assert 'product_id' in response.json
    assert response.json['message'] == f'Product "{data["productname"]}" created successfully'

def test_create_product_missing_image(client):
    # Create a sample product data without an image
    data = {
        'productname': 'Test Product',
        'description': 'This is a test product',
        'price': '19.99',
        'category_id': '1'
    }
    
    # Send a POST request to the create_product endpoint
    response = client.post('/api/products', data=data)

    # Assert the response
    assert response.status_code == 400
    assert response.json['message'] == 'No image part in the request'

def test_create_product_invalid_image_format(client):
    # Create a sample product data with an invalid image format
    data = {
        'productname': 'Test Product',
        'description': 'This is a test product',
        'price': '19.99',
        'category_id': '1'
    }
    image_data = (io.BytesIO(b"fake image data"), 'test.txt')  # Invalid format
    
    # Send a POST request to the create_product endpoint
    response = client.post('/api/products', data={
        **data,
        'image': image_data
    }, content_type='multipart/form-data')

    # Assert the response
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid image format'