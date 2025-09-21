class Retrieval:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
    
    def search_products(self, query, limit=5):
        results = self.vectorstore.search(query, limit)
        
        products = []
        for result in results:
            product = {
                'score': result.score,
                'content': result.payload['page_content'],
                'metadata': result.payload['metadata']
            }
            products.append(product)
        
        return products
    
    def get_similar_products(self, product_id, limit=5):
        query = f"product_id:{product_id}"
        return self.search_products(query, limit)
    
    def search_by_category(self, category, limit=10):
        query = f"category:{category}"
        return self.search_products(query, limit)
    
    def search_by_price_range(self, min_price, max_price, limit=10):
        query = f"price between {min_price} and {max_price}"
        return self.search_products(query, limit)
