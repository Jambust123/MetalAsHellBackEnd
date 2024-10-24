class Category:
    def __init__(self, categoryid, categoryname):
        self.categoryid = categoryid
        self.categoryname = categoryname

    @classmethod
    def create_table(cls):
        return """
        CREATE TABLE IF NOT EXISTS categories (
            categoryid SERIAL PRIMARY KEY,
            categoryname VARCHAR(50) UNIQUE NOT NULL
        );
        """
