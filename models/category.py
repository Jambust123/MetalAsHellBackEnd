class Category:
    def __init__(self, categoryid, categoryname):
        self.categoryid = categoryid
        self.categoryname = categoryname

    @classmethod
    def create_table(cls):
        return """
        CREATE TABLE IF NOT EXISTS categories (
            categoryid SERIAL PRIMARY KEY,
            categoryname VARCHAR(100) UNIQUE NOT NULL
        );
        """

    @classmethod
    def seed_categories(cls):
        return """
        INSERT INTO categories (categoryname) VALUES
            ('bracelets'),
            ('earrings'),
            ('necklaces'),
            ('other')
        ON CONFLICT (categoryname) DO NOTHING;
        """
    
    def __repr__(self):
        return f"Category(id={self.categoryid}, name={self.categoryname})"
