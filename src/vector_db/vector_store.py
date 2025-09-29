import uuid
from typing import List, Dict, Any, Optional
import sqlite3
import json
from bs4 import BeautifulSoup
from qdrant_client import QdrantClient
from qdrant_client.http import models
from .embedding import faq_embedding_model, product_embedding_model
from .config import config


class VectorStore:

    
    def __init__(self, qdrant_url: str, qdrant_api_key: str, collection_name: str = "documents"):
        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key
        )
        self.collection_name = collection_name
        
        # Use appropriate embedding model based on collection name
        if collection_name == config.FAQ_COLLECTION:
            self.embedding_model = faq_embedding_model
            self.vector_size = config.FAQ_VECTOR_SIZE
        else:
            self.embedding_model = product_embedding_model
            self.vector_size = config.PRODUCT_VECTOR_SIZE
    
    def load_product_data_from_db(self, db_path: str) -> List[Dict[str, Any]]:
        """Load product data from SQLite database."""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
        SELECT
            id, category, sub_category, title, sale_price, original_price,
            available_sizes, product_url, image_url, product_details_json, title_masri
        FROM products
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        products = [dict(row) for row in rows]
        conn.close()
        
        return products
    
    def parse_specs_html(self, html_string: str) -> str:
        """Parse HTML specs to plain text."""
        if not html_string or not isinstance(html_string, str): 
            return ""
        soup = BeautifulSoup(html_string, 'html.parser')
        return soup.get_text(separator=', ', strip=True)
    
    def create_page_content(self, product: dict) -> str:
        """
        Creates a very rich text summary for multilingual semantic search.
        """
        content = f"Product Name: {product.get('title', '')}\n"
        if product.get('title_masri'):
            content += f"Name in Masri: {product.get('title_masri')}\n"
        
        content += f"Category: {product.get('category', '')}, {product.get('sub_category', '')}\n"
        
        # Safely parse the JSON details string
        details = {}
        if product.get('product_details_json'):
            try:
                details = json.loads(product['product_details_json'])
            except (json.JSONDecodeError, TypeError):
                details = {}
        
        # Extract and add color information to the content
        colors_list = details.get('colors', [])
        if colors_list and isinstance(colors_list, list):
            # Extract color names like 'Black', 'Dark Blue', 'Red'
            color_names = [color.get('name') for color in colors_list if color.get('name')]
            if color_names:
                content += f"Available Colors: {', '.join(color_names)}\n"

        # Extract and clean specs from the nested HTML in the JSON
        specs_html = details.get('specs', {}).get('raw_html', '')
        specs_text = self.parse_specs_html(specs_html)
        if specs_text:
            content += f"Specifications: {specs_text}\n"
            
        return content
    
    def create_metadata(self, product: dict) -> dict:
        """
        Creates a structured metadata dictionary.
        """
        metadata = {
            'title': product.get('title'),
            'category': product.get('category'),
            'sub_category': product.get('sub_category'),
            'sale_price': product.get('sale_price'),
            'original_price': product.get('original_price'),
            'currency': product.get('currency'),
            'product_url': product.get('product_url'),
            'image_url': product.get('image_url'),
            'available_sizes': product.get('available_sizes'),
            'product_details_json': product.get('product_details_json')
        }
        return metadata
    
    def chunk_products(self, products: list) -> List[Dict[str, Any]]:
        """Processes a list of products into RAG-ready chunks."""
        chunks = []
        for product in products:
            page_content = self.create_page_content(product)
            metadata = self.create_metadata(product)
            chunk = {'content': page_content, 'metadata': metadata}
            chunks.append(chunk)
        return chunks
    
    def create_collection(self, vector_size: int = None, distance: models.Distance = models.Distance.COSINE) -> bool:
        # Use the vector size for this collection type if not explicitly provided
        if vector_size is None:
            vector_size = self.vector_size
            
        try:
            self.client.get_collection(collection_name=self.collection_name)
            print(f"Collection '{self.collection_name}' already exists.")
            return True
        except Exception as e:
            try:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=distance
                    )
                )
                print(f"Collection '{self.collection_name}' created successfully.")
                return True
            except Exception as create_error:
                print(f"Error creating collection '{self.collection_name}': {create_error}")
                return False
    
    def store_documents(self, documents: List[Dict[str, Any]], batch_size: int = 64) -> bool:
        try:
            if not self.create_collection():
                return False
            
            points = []
            for doc in documents:
                embedding = self.embedding_model.embed_query(doc['content'])
                
                point = models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        'content': doc['content'],
                        'metadata': doc.get('metadata', {})
                    }
                )
                points.append(point)
            
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                print(f"✅ Inserted batch {i // batch_size + 1}/{(len(points) - 1) // batch_size + 1}")
            
            print(f"Successfully stored {len(documents)} documents in '{self.collection_name}' collection.")
            return True
            
        except Exception as e:
            print(f"Error storing documents: {e}")
            return False
    
    def search(self, query: str, limit: int = 10) -> List[models.ScoredPoint]:
        try:
            query_embedding = self.embedding_model.embed_query(query)
            
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=limit
            )
            
            return search_result.points
            
        except Exception as e:
            print(f"Error performing search: {e}")
            return []