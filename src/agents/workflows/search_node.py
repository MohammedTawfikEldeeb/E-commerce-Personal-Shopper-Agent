from src.agents.schemas.agent_state import AgentState 
from src.agents.tools.product_search import product_search_tool

def search_node(state: AgentState)-> dict:
    """This node performs the product search with conversation awareness"""
    print("--- Executing Conversation-Aware Search Node ---")
    last_query = state.messages[-1].content
    
    # Get conversation history from the state
    conversation_history = getattr(state, "prior_conversation", "")
    
    # Use the product search tool with conversation history
    search_results = product_search_tool.invoke({
        "query": last_query,
        "conversation_history": conversation_history
    })
    
    return {"search_results": search_results}