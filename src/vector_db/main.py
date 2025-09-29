import os
import sys
import json

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from vector_db.vector_store import VectorStore
from vector_db.config import config
from vector_db.utils import load_faq_data, process_faq_documents

def load_faq_documents(faq_data_path: str) -> list:
    """Load and process FAQ documents."""
    print(f"Loading FAQ data from {faq_data_path}...")
    faq_data = load_faq_data(faq_data_path)
    print(f"Loaded {len(faq_data)} FAQ entries")
    
    # Process FAQ data into documents
    faq_documents = process_faq_documents(faq_data)
    print(f"Processed {len(faq_documents)} FAQ documents")
    
    return faq_documents

def main():
    print("Starting vector database population process...")
    
    # Load and store product data
    print("\n=== Processing Product Data ===")
    product_vector_store = VectorStore(
        qdrant_url=config.QDRANT_URL,
        qdrant_api_key=config.QDRANT_API_KEY,
        collection_name=config.PRODUCT_COLLECTION
    )
    
    # Load product data from database
    db_path = "db/ecommerce_products.db"
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}")
    
    print("Loading product data from database...")
    products = product_vector_store.load_product_data_from_db(db_path)
    print(f"Loaded {len(products)} products from database")
    
    # Process products into chunks
    print("Processing products into chunks...")
    product_chunks = product_vector_store.chunk_products(products)
    print(f"Created {len(product_chunks)} product chunks")
    
    # Store product documents in vector database
    print("Storing product documents in vector database...")
    product_success = product_vector_store.store_documents(product_chunks, batch_size=config.BATCH_SIZE)
    
    if product_success:
        print("Successfully stored all products in vector database")
    else:
        print("Failed to store products in vector database")
    
    # Load and store FAQ data
    print("\n=== Processing FAQ Data ===")
    faq_vector_store = VectorStore(
        qdrant_url=config.QDRANT_URL,
        qdrant_api_key=config.QDRANT_API_KEY,
        collection_name=config.FAQ_COLLECTION
    )
    
    # Load FAQ data
    faq_data_path = "data/raw/faq_data.json"
    if not os.path.exists(faq_data_path):
        raise FileNotFoundError(f"FAQ data file not found at {faq_data_path}")
    
    faq_documents = load_faq_documents(faq_data_path)
    
    # Store FAQ documents in vector database
    print("Storing FAQ documents in vector database...")
    faq_success = faq_vector_store.store_documents(faq_documents, batch_size=config.BATCH_SIZE)
    
    if faq_success:
        print("Successfully stored all FAQ documents in vector database")
    else:
        print("Failed to store FAQ documents in vector database")
    
    # Summary
    print("\n=== Process Summary ===")
    if product_success and faq_success:
        print("✅ All data successfully stored in vector database")
    else:
        print("❌ Some errors occurred during the process")
        if not product_success:
            print("   - Product data storage failed")
        if not faq_success:
            print("   - FAQ data storage failed")

if __name__ == "__main__":
    main()