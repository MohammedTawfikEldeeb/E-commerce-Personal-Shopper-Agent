from langchain_core.tools import tool
from src.agents import config
from src.agents.schemas.tool_schemas import ProductSearchInput
from src.vector_db.vector_store import VectorStore
from src.vector_db.search import ProductSearch

product_vector_store = VectorStore(
    qdrant_url=config.QDRANT_URL,
    qdrant_api_key=config.QDRANT_API_KEY,
    collection_name="sutra_db"
)

product_search = ProductSearch(product_vector_store)

@tool("product-search-tool", args_schema=ProductSearchInput)
def product_search_tool(query: str, conversation_history: str = "")-> list:
    """Searches for products in the vector database with conversation context awareness"""
    # If we have conversation history, let the LLM refine the query using context
    if conversation_history:
        # Use the conversation history to refine the query
        refined_query = refine_query_with_context(query, conversation_history)
        return product_search.search(refined_query, limit=10)
    else:
        # Direct search without context
        return product_search.search(query, limit=10)

def refine_query_with_context(query: str, conversation_history: str) -> str:
    """
    Use the conversation history to refine the query if needed
    """
    # Check if this is a vague query that needs context
    if is_vague_query(query):
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            api_key=config.GOOGLE_API_KEY,
            model="gemini-2.5-flash-lite"
        )
        
        refinement_prompt = f"""
You are an e-commerce search assistant. The user has made a request that needs clarification using conversation context.

Conversation History:
{conversation_history}

Current Request: "{query}"

Instructions:
1. Analyze the conversation history to understand what products were previously discussed
2. If the current request is vague (like "مفيش سعر اقل من كده"), understand what the user means in context
3. Create a specific search query that addresses the user's intent

Examples:
- Previous: "عاوز بنطلون جينز" -> Current: "مفيش سعر اقل من كده" -> Output: "بنطلون جينز اقل من 200 جنيه"
- Previous: "تيشيرت أحمر" -> Current: "غيرها" -> Output: "تيشيرت ألوان مختلفة"

Respond ONLY with the refined search query, nothing else.
"""
        
        try:
            refined_query = llm.invoke(refinement_prompt).content.strip()
            print(f"Refined query: '{query}' -> '{refined_query}'")
            return refined_query
        except Exception as e:
            print(f"Error refining query: {e}")
            # Fallback to original query
            return query
    
    # If not a vague query, return as is
    return query

def is_vague_query(query: str) -> bool:
    """
    Check if a query is vague and needs context from conversation history.
    """
    vague_keywords = [
        "something else", "another one", "show me more", "different", 
        "other options", "more choices", "alternatives", "similar",
        "غير كده", "تانية", "غيرها", "اختيارات اكتر", "اختيارات تانية",
        "حاجة تانية", " الحاجات الشبيهة", "منتجات مشابهة", "مختلف", 
        "خيارات اكتر", "اختيار ثاني", "منتج تاني", "موديل تاني", "شوفلي حاتجة تانية",
        "مفيش سعر اقل", "سعر اقل", "اقل من كده", "اقل من ذلك"
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in vague_keywords)