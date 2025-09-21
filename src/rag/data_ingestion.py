import sqlite3
import json

class DataIngestion:
    def __init__(self, db_path="db/ecommerce_products.db"):
        self.db_path = db_path
    
    def safe_json_loads(self, value):
        if not value:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            cleaned = value.replace("'", '"')
            try:
                return json.loads(cleaned)
            except Exception:
                return value
    
    def get_all_products(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
        SELECT id, product_id, pid, title, brand, category, sub_category,
               description, actual_price, selling_price, discount_percentage,
               average_rating, out_of_stock, seller, url, images, 
               product_details, crawled_at
        FROM products
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        products = []
        for row in rows:
            product = {
                'id': row['id'],
                'product_id': row['product_id'],
                'pid': row['pid'],
                'title': row['title'],
                'brand': row['brand'],
                'category': row['category'],
                'sub_category': row['sub_category'],
                'description': row['description'],
                'actual_price': row['actual_price'],
                'selling_price': row['selling_price'],
                'discount_percentage': row['discount_percentage'],
                'average_rating': row['average_rating'],
                'out_of_stock': row['out_of_stock'],
                'seller': row['seller'],
                'url': row['url'],
                'images': self.safe_json_loads(row['images']) if row['images'] else None,
                'product_details': self.safe_json_loads(row['product_details']) if row['product_details'] else None,
                'crawled_at': row['crawled_at']
            }
            products.append(product)
        
        conn.close()
        return products