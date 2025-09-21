from src.rag import DataIngestion
from src.rag import Chunking
from src.rag import VectorStore
from src.rag import Retrieval
from src.rag import config
def main():
    QDRANT_URL = config.QDRANT_URL
    QDRANT_API_KEY = config.QDRANT_API_KEY
    
    ingestion = DataIngestion()
    chunking = Chunking()
    vectorstore = VectorStore(QDRANT_URL, QDRANT_API_KEY)
    retrieval = Retrieval(vectorstore)
    
    print("Loading products from database...")
    products = ingestion.get_all_products()
    
    print("Creating chunks...")
    chunks = chunking.chunk_products(products)
    
    print("Storing in vector database...")
    vectorstore.store_chunks(chunks)
    
    print("Testing retrieval...")
    results = retrieval.search_products("men's t-shirt", limit=3)
    
if __name__ == "__main__":
    main()
