from utils.db import connection_pool

def get_categories():
    try:
        with connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM categories;")
                categories = cursor.fetchall()

        if categories:
            result = []
            for category in categories:
                result.append({
                    'category_id': category[0],
                    'categoryname': category[1]
                })

            return {'categories': result}, 200
        else:
            return {'message': 'No categories found'}, 404
    except Exception as e:
        return {'message': 'Internal Server Error'}, 500
