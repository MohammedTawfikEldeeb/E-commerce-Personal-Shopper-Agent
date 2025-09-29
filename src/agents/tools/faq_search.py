from langchain_core.tools import tool
from src.vector_db.vector_store import VectorStore
from src.vector_db.search import FAQSearch
from src.agents import config
from src.agents.schemas.tool_schemas import FAQSearchInput

# Initialize the FAQ vector store and search components
# Using the "sutran_faq" collection that was created in the notebook
faq_vector_store = VectorStore(
    qdrant_url=config.QDRANT_URL,
    qdrant_api_key=config.QDRANT_API_KEY,
    collection_name="sutran_faq"
)

faq_search = FAQSearch(faq_vector_store)

@tool("faq-search-tool", args_schema=FAQSearchInput)
def faq_search_tool(query: str) -> list:
    """
    Searches for FAQ entries in the FAQ vector database.
    
    Args:
        query (str): The user's FAQ query
        
    Returns:
        list: Search results from the FAQ vector database
    """
    print(f"Searching FAQ database for: '{query}'")
    
    # Perform the FAQ search using the new vector database modules
    search_results = faq_search.search(query, limit=3)
    
    return search_results