class Product:
    def __init__(self, productid, productname, description, price, categoryid=None):
        self.productid = productid
        self.productname = productname
        self.description = description
        self.price = price
        self.categoryid = categoryid

    @classmethod
    def create_table(cls):
        return """
        CREATE TABLE IF NOT EXISTS products (
            productid SERIAL PRIMARY KEY,
            productname VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            categoryid INTEGER REFERENCES categories(categoryid) ON DELETE SET NULL
        );
        """
