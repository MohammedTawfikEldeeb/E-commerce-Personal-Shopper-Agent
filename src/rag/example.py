from data_ingestion import DataIngestion
from chunking import Chunking
from vectorstore import VectorStore
from retrieval import Retrieval
from config import QDRANT_URL, QDRANT_API_KEY

def setup_rag():
    ingestion = DataIngestion()
    chunking = Chunking()
    vectorstore = VectorStore(QDRANT_URL, QDRANT_API_KEY)
    retrieval = Retrieval(vectorstore)
    
    return ingestion, chunking, vectorstore, retrieval

def load_and_store_data(ingestion, chunking, vectorstore):
    products = ingestion.get_all_products()
    chunks = chunking.chunk_products(products[:1000])
    vectorstore.store_chunks(chunks)

def search_examples(retrieval):
    queries = [
        "men's t-shirt under 500",
        "women's shoes",
        "electronics",
        "branded watches"
    ]
    
    for query in queries:
        print(f"\nSearching for: {query}")
        results = retrieval.search_products(query, limit=3)
        
        for result in results:
            print(f"Score: {result['score']:.3f}")
            print(f"Brand: {result['metadata']['brand']}")
            print(f"Price: ₹{result['metadata']['selling_price']}")
            print("---")

if __name__ == "__main__":
    ingestion, chunking, vectorstore, retrieval = setup_rag()
    
    print("Loading and storing data...")
    load_and_store_data(ingestion, chunking, vectorstore)
    
    print("Testing search...")
    search_examples(retrieval)
