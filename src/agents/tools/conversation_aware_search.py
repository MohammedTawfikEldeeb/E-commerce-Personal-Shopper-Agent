from langchain_core.tools import tool
from src.agents import config
from src.agents.schemas.tool_schemas import ProductSearchInput
from langchain_google_genai import ChatGoogleGenerativeAI
from src.vector_db.vector_store import VectorStore
from src.vector_db.search import ProductSearch
import re

product_vector_store = VectorStore(
    qdrant_url=config.QDRANT_URL,
    qdrant_api_key=config.QDRANT_API_KEY,
    collection_name="sutra_db"
)

product_search = ProductSearch(product_vector_store)

llm = ChatGoogleGenerativeAI(
    api_key=config.GOOGLE_API_KEY,
    model="gemini-2.5-flash-lite"
)

def is_vague_query(query: str) -> bool:
    """
    Check if a query is vague and needs context from conversation history.
    
    Args:
        query (str): The user's query
        
    Returns:
        bool: True if the query is vague, False otherwise
    """
    vague_keywords = [
        "something else", "another one", "show me more", "different", 
        "other options", "more choices", "alternatives", "similar",
        "غير كده", "تانية", "غيرها", "اختيارات اكتر", "اختيارات تانية",
        "حاجة تانية", " الحاجات الشبيهة", "منتجات مشابهة", "مختلف", 
        "خيارات اكتر", "اختيار ثاني", "منتج تاني", "موديل تاني", "شوفلي حاتجة تانية"
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in vague_keywords)

def refine_query_with_context(query: str, conversation_history: str) -> str:
    """
    Use an LLM to refine a vague query using conversation context.
    
    Args:
        query (str): The vague query to refine
        conversation_history (str): The recent conversation history
        
    Returns:
        str: The refined query
    """
    # If the query is not vague, return it as is
    if not is_vague_query(query):
        return query
    
    # Create a prompt to refine the vague query using conversation context
    refinement_prompt = f"""
You are an expert e-commerce search assistant helping customers find products.
The user has made a vague request that needs clarification using conversation context.

Conversation History:
{conversation_history}

Vague Request: "{query}"

Instructions:
1. Analyze the conversation history to understand what products were previously discussed
2. Identify the category or type of products the user was interested in
3. If the user is asking for "something else" or similar phrases, they want alternatives to previously shown products
4. Create a specific search query that finds similar or alternative products in the same category

Examples:
- Previous: "عاوز تيشيرت" -> Current: "شوفلي حاتجة تانية" -> Output: "تيشيرت ألوان مختلفة"
- Previous: "عاوز شوز" -> Current: "غيرها" -> Output: "شوز تصميم مختلف"
- Previous: "تيشيرت أحمر" -> Current: "تانية" -> Output: "تيشيرت ألوان أخرى"

Respond ONLY with the refined search query in the same language as the user's request, nothing else.
"""
    
    try:
        # Use the LLM to refine the query
        refined_query = llm.invoke(refinement_prompt).content.strip()
        print(f"Refined query: '{query}' -> '{refined_query}'")
        return refined_query
    except Exception as e:
        print(f"Error refining query: {e}")
        # Fallback: return a general query for similar items if refinement fails
        return "منتجات مشابهة"

@tool("conversation-aware-product-search-tool", args_schema=ProductSearchInput)
def conversation_aware_product_search_tool(query: str, conversation_history: str = "") -> list:
    """
    Searches for products in the vector database with conversation context awareness.
    
    This tool maintains conversation memory and refines vague queries using context.
    
    Args:
        query (str): The user's search query
        conversation_history (str): Recent conversation history for context
        
    Returns:
        list: Search results from the vector database
    """
    print(f"Original query: '{query}'")
    
    # Check if the query is vague and needs refinement
    if is_vague_query(query) and conversation_history:
        # Refine the query using conversation context
        refined_query = refine_query_with_context(query, conversation_history)
        print(f"Using refined query: '{refined_query}'")
        # Use the refined query for search
        search_query = refined_query
    else:
        # Use the original query for search
        search_query = query
    
    # Perform the product search using the new vector database modules
    search_results = product_search.search(search_query, limit=10)
    
    return search_results