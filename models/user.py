from psycopg2 import sql

class User:
    def __init__(self, userid, username, email, password, is_admin=False):
        self.userid = userid
        self.username = username
        self.email = email
        self.password = password
        self.is_admin = is_admin

    @classmethod
    def create_table(cls):
        return """
        CREATE TABLE IF NOT EXISTS users (
            userid SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE
        );
        """
