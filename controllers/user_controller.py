from flask import request
from psycopg2 import pool
from werkzeug.security import generate_password_hash
from models.user import User
from utils.db import connection_pool 

# Create user function (already provided)
def create_user():
    data = request.get_json()
    if not data:
        return {'message': 'No input data provided'}, 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return {'message': 'Username, email, and password are required'}, 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    with connection_pool.getconn() as conn:
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

    return {'user_id': user_id, 'message': f'User "{username}" created successfully'}, 201

# Get all users function
def get_users():
    try:
        with connection_pool.getconn() as conn:
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
        return {'message': 'Internal Server Error'}, 500

# Get user by username function
def get_user_by_username(username):
    try:
        with connection_pool.getconn() as conn:
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
        return {'message': 'Internal Server Error'}, 500
