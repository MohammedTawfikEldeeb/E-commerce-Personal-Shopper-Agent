from src.agents.schemas.agent_state import AgentState
from langchain_core.messages import AIMessage, HumanMessage

def load_conversation_memory(state: AgentState) -> dict:
    """
    Load and format the last 4 messages from conversation history
    This runs at the beginning of each conversation turn
    """
    print("--- Loading Conversation Memory ---")
    
    # Get the last 4 messages (or all if less than 4)
    last_msgs = state.messages[-4:] if len(state.messages) >= 4 else state.messages
    
    conversation = []
    for message in last_msgs:
        if message.type == "human":
            conversation.append(f"HUMAN: {message.content}")
        elif message.type == "ai":
            conversation.append(f"AI: {message.content}")
    
    formatted_conversation = "\n".join(conversation)
    
    print(f"Loaded conversation context: {len(last_msgs)} messages")
    
    return {"prior_conversation": formatted_conversation}


def update_conversation_memory(state: AgentState) -> dict:
    """
    Update the conversation memory with the latest exchange
    This runs at the end of each conversation turn
    """
    print("--- Updating Conversation Memory ---")
    
    if len(state.messages) >= 2:
        user_query = state.messages[-2].content if state.messages[-2].type == "human" else ""
        ai_response = state.messages[-1].content if state.messages[-1].type == "ai" else ""
        
        updated_conversation = (
            f"{state.prior_conversation}\n"
            f"HUMAN: {user_query}\n"
            f"AI: {ai_response}"
        ).strip()
        
        lines = updated_conversation.split("\n")
        if len(lines) > 8:  
            lines = lines[-8:]  
            updated_conversation = "\n".join(lines)
        
        print("Memory updated with latest exchange")
        
        return {"prior_conversation": updated_conversation}
    
    return {"prior_conversation": state.prior_conversation}