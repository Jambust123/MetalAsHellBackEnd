from flask import request
from werkzeug.security import generate_password_hash
import logging
from utils.db import connection_pool

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def create_user():
    try:
        # Get the JSON data from the request
        data = request.get_json()

        # Validate that we received data
        if not data:
            logging.error("No input data provided.")
            return {'message': 'No input data provided'}, 400

        # Extract required fields from the request
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        is_admin = data.get('is_admin', False)  # Default to False if not provided

        # Validate required fields
        if not username or not email or not password:
            logging.error(f"Missing fields: username={username}, email={email}, password={password}")
            return {'message': 'Username, email, and password are required'}, 400

        # Hash the password using werkzeug security
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Use connection pool to get a DB connection
        with connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                # Check if the username already exists in the database
                cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s;", (username,))
                if cursor.fetchone()[0] > 0:
                    logging.error(f"Username '{username}' already exists.")
                    return {'message': 'Username already exists'}, 400

                # Check if the email already exists in the database
                cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s;", (email,))
                if cursor.fetchone()[0] > 0:
                    logging.error(f"Email '{email}' already exists.")
                    return {'message': 'Email already exists'}, 400

                # Insert the new user into the database
                cursor.execute("""
                    INSERT INTO users (username, email, password, is_admin)
                    VALUES (%s, %s, %s, %s) RETURNING userid;
                """, (username, email, hashed_password, is_admin))

                # Get the user ID of the newly created user
                user_id = cursor.fetchone()[0]
                conn.commit()

                logging.info(f"User '{username}' created successfully with user ID {user_id}.")

        # Return success response
        return {'user_id': user_id, 'message': f'User "{username}" created successfully'}, 201

    except Exception as e:
        # Log the error for debugging purposes
        logging.error(f"Error creating user: {str(e)}")
        return {'message': 'Internal Server Error'}, 500


# Get all users function
def get_users():
    try:
        with connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT userid, username, email, is_admin FROM users;")
                users = cursor.fetchall()

        if users:
            user_list = []
            for user in users:
                user_list.append({
                    'user_id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'is_admin': user[3]
                })
            return {'users': user_list}, 200
        else:
            return {'message': 'No users found'}, 404
    except Exception as e:
        return {'message': 'Internal Server Error'}, 500

# Get user by username function
def get_user_by_username(username):
    try:
        with connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT userid, username, email, is_admin FROM users WHERE username = %s;", (username,))
                user = cursor.fetchone()

        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'is_admin': user[3]
            }, 200
        else:
            return {'message': 'User not found'}, 404
    except Exception as e:
        return {'message': 'Internal Server Error'}, 500

def create_users():
    data = request.get_json()
    if not data or not isinstance(data, list):
        return {'message': 'Input data must be a list of users'}, 400

    results = []  # To store the result of each user creation
    with connection_pool.getconn() as conn:
        with conn.cursor() as cursor:
            for user_data in data:
                username = user_data.get('username')
                email = user_data.get('email')
                password = user_data.get('password')
                is_admin = user_data.get('is_admin', False)

                # Validate required fields
                if not username or not email or not password:
                    results.append({'username': username, 'status': 'failed', 'message': 'Username, email, and password are required'})
                    continue

                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

                # Check for existing username
                cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s;", (username,))
                if cursor.fetchone()[0] > 0:
                    results.append({'username': username, 'status': 'failed', 'message': 'Username already exists'})
                    continue

                # Check for existing email
                cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s;", (email,))
                if cursor.fetchone()[0] > 0:
                    results.append({'username': username, 'status': 'failed', 'message': 'Email already exists'})
                    continue

                # Insert new user
                cursor.execute("""
                    INSERT INTO users (username, email, password, is_admin)
                    VALUES (%s, %s, %s, %s) RETURNING userid;
                """, (username, email, hashed_password, is_admin))
                user_id = cursor.fetchone()[0]
                conn.commit()

                results.append({'username': username, 'status': 'success', 'user_id': user_id})

    return {'results': results}, 201