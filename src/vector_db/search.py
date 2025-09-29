
from typing import List, Dict, Any, Optional
from sentence_transformers import CrossEncoder
from qdrant_client.http import models
from .vector_store import VectorStore


class SemanticSearch:

    
    def __init__(self, vector_store: VectorStore, use_reranking: bool = True):

        self.vector_store = vector_store
        self.use_reranking = use_reranking
        
        if use_reranking:
            self.reranker = CrossEncoder('BAAI/bge-reranker-base')
    
    def search(self, query: str, limit: int = 5, initial_limit: Optional[int] = None) -> List[Dict[str, Any]]:

        if initial_limit is None:
            initial_limit = min(50, limit * 3) if self.use_reranking else limit
        
        initial_results = self.vector_store.search(query, initial_limit)
        
        if self.use_reranking and len(initial_results) > limit:
            reranked_results = self._rerank(query, initial_results)
            final_results = reranked_results[:limit]
        else:
            final_results = initial_results[:limit]
        
        formatted_results = []
        for result in final_results:
            formatted_result = {
                'score': result.score,
                'content': result.payload.get('content', ''),
                'metadata': result.payload.get('metadata', {})
            }
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def _rerank(self, query: str, results: List[models.ScoredPoint]) -> List[models.ScoredPoint]:

        if not results:
            return []
        
        pairs = [[query, result.payload.get('content', '')] for result in results]
        scores = self.reranker.predict(pairs)
        
        reranked = list(zip(scores, results))
        reranked.sort(key=lambda x: x[0], reverse=True)
        
        return [result for score, result in reranked]


class ProductSearch(SemanticSearch):

    
    def __init__(self, vector_store: VectorStore):
        super().__init__(vector_store, use_reranking=True)


class FAQSearch(SemanticSearch):

    
    def __init__(self, vector_store: VectorStore):
        super().__init__(vector_store, use_reranking=False)