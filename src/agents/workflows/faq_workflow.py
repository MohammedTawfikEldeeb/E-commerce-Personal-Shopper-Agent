from src.agents.schemas.agent_state import AgentState
from src.agents import config
from qdrant_client import QdrantClient
from langchain_community.embeddings import HuggingFaceEmbeddings

qdrant_client = QdrantClient(
    url=config.QDRANT_URL,
    api_key=config.QDRANT_API_KEY
)

embedding_model = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-small")

def faq_node(state: AgentState) -> dict:
    """
    Handles FAQ intents by searching the FAQ vector store and passing results to generator.
    """
    print("--- Executing FAQ Node ---")
    
    user_query = state.messages[-1].content
    
    query_embedding = embedding_model.embed_query(user_query)
    
    search_results = qdrant_client.search(
        collection_name="faq",
        query_vector=query_embedding,
        limit=3
    )
    
    # Convert search results to the format expected by the generator
    faq_results = []
    for result in search_results:
        faq_item = {
            'score': result.score,
            'content': result.payload['content'],
            'metadata': result.payload['metadata']
        }
        faq_results.append(faq_item)
    
    return {
        "route": "faq",
        "search_results": faq_results,
        "filtered_results": faq_results
    }