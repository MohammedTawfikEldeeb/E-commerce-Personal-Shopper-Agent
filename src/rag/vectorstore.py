import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
from langchain_community.embeddings import HuggingFaceEmbeddings

class VectorStore:
    def __init__(self, qdrant_url, qdrant_api_key, collection_name="products"):
        self.qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key
        )
        self.embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.collection_name = collection_name
    
    def create_collection(self):
        try:
            self.qdrant_client.get_collection(collection_name=self.collection_name)
            print(f"Collection '{self.collection_name}' already exists.")
        except Exception:
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,  # Dimension for all-MiniLM-L6-v2
                    distance=models.Distance.COSINE
                )
            )
            print(f"Collection '{self.collection_name}' created.")
    
    def store_chunks(self, chunks):
        self.create_collection()
        
        points = []
        for chunk in chunks:
            embedding = self.embedding_model.embed_query(chunk['page_content'])
            
            point = models.PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    'page_content': chunk['page_content'],
                    'metadata': chunk['metadata']
                }
            )
            points.append(point)
        
        # Batching loop is now outside the main loop
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=batch,
                wait=True # Wait for the operation to complete
            )
            print(f"✅ Inserted batch {i//batch_size + 1}")
            
    def search(self, query, limit=5):
        # Correctly calling the embedding model's method
        query_embedding = self.embedding_model.embed_query(query)
        
        results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit
        )
        
        return results