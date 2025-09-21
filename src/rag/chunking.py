import json

class Chunking:
    def __init__(self):
        pass
    
    @staticmethod
    def create_page_content(product):
        content = f"Title: {product['title']}\n"
        
        if product['description']:
            content += f"Description: {product['description']}\n"
        
        content += f"Category: {product['category']}\n"
        content += f"Sub Category: {product['sub_category']}\n"
        
        if product['brand']:
            content += f"Brand: {product['brand']}\n"
        
        if product['selling_price']:
            content += f"Price: ₹{product['selling_price']}\n"
        
        if product['average_rating']:
            content += f"Rating: {product['average_rating']}/5\n"
        
        if product['seller']:
            content += f"Seller: {product['seller']}\n"
        
        if product['product_details']:
            content += "Product Details:\n"
            
            details = product['product_details']
            if isinstance(details, str):
                try:
                    details = json.loads(details) 
                except:
                    details = [details]
            
            if isinstance(details, dict):
                details = [details]
            
            if isinstance(details, list):
                for detail in details:
                    if isinstance(detail, dict):
                        for key, value in detail.items():
                            content += f"{key}: {value}\n"
                    else:
                        content += f"- {detail}\n"
        
        return content
        
    @staticmethod
    def create_metadata(product):
        metadata = {
            'product_id': product['product_id'],
            'pid': product['pid'],
            'category': product['category'],
            'sub_category': product['sub_category'],
            'brand': product['brand'],
            'selling_price': product['selling_price'],
            'average_rating': product['average_rating'],
            'out_of_stock': product['out_of_stock'],
            'seller': product['seller'],
            'images': product['images'],
            'url': product['url']
        }
        return metadata
    
    @staticmethod
    def chunk_products(products):
        chunks = []
        
        for product in products:
            # Call the other static methods using the class name
            page_content = Chunking.create_page_content(product)
            metadata = Chunking.create_metadata(product)
            
            chunk = {
                'page_content': page_content,
                'metadata': metadata
            }
            chunks.append(chunk)
        
        return chunks