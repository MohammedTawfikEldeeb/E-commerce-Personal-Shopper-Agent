import json
from typing import List, Dict, Any


def load_faq_data(file_path: str) -> List[Dict[str, Any]]:

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading FAQ data from {file_path}: {e}")
        return []


def process_faq_documents(faq_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    documents = []
    
    for entry in faq_data:
        content = f"Question: {entry['question']}\nAnswer: {entry['answer']}"
        
        document = {
            'content': content,
            'metadata': entry.get('metadata', {})
        }
        
        documents.append(document)
    
    return documents


def process_product_documents(product_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    documents = []
    
    for product in product_data:
        content_parts = []
        
        if product.get('title'):
            content_parts.append(f"Title: {product['title']}")
            
        if product.get('description'):
            content_parts.append(f"Description: {product['description']}")
            
        if product.get('category'):
            content_parts.append(f"Category: {product['category']}")
            
        if product.get('sub_category'):
            content_parts.append(f"Sub-category: {product['sub_category']}")
            
        if product.get('brand'):
            content_parts.append(f"Brand: {product['brand']}")
            
        if product.get('selling_price'):
            content_parts.append(f"Price: {product['selling_price']}")
        
        content = "\n".join(content_parts)
        
        document = {
            'content': content,
            'metadata': {
                'title': product.get('title', ''),
                'category': product.get('category', ''),
                'sub_category': product.get('sub_category', ''),
                'brand': product.get('brand', ''),
                'selling_price': product.get('selling_price', ''),
                'sale_price': product.get('sale_price', ''),
                'currency': product.get('currency', ''),
                'product_url': product.get('product_url', ''),
                'image_url': product.get('image_url', ''),
                'available_sizes': product.get('available_sizes', ''),
                'product_details_json': product.get('product_details_json', ''),
                'doc_type': 'product'
            }
        }
        
        documents.append(document)
    
    return documents