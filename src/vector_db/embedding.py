
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import List, Union


class EmbeddingModel:
    
    def __init__(self, model_name: str = "intfloat/multilingual-e5-large"):
        self.model_name = model_name
        self.model = HuggingFaceEmbeddings(model_name=model_name)
    
    def embed_query(self, text: str) -> List[float]:
        return self.model.embed_query(text)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.embed_documents(texts)


# Default embedding models
faq_embedding_model = EmbeddingModel("intfloat/multilingual-e5-small")
product_embedding_model = EmbeddingModel("intfloat/multilingual-e5-large")