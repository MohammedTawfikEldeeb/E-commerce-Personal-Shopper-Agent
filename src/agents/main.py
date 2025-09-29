# main.py
from src.agents.graph import app
from langchain_core.messages import HumanMessage, AIMessage # 👈 Import AIMessage

def main():
    print("E-commerce Agent is ready. Type 'exit' to quit.")
    # We create a message history list to maintain the conversation
    message_history = []
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        
        # Add the new user message to the history
        message_history.append(HumanMessage(content=user_input))
        
        # Pass the entire conversation history to the agent
        inputs = {"messages": message_history}
        
        response = app.invoke(inputs)
        
        # Update our history with the agent's response
        message_history = response.get("messages", [])
        
        print("Agent Response:")
        # Check if the last message is from the AI and print its content
        if message_history and isinstance(message_history[-1], AIMessage):
            print(message_history[-1].content)
        else:
            # Fallback for workflows that don't add an AIMessage
            # (like our current search_node)
            print(response.get("search_results", "Sorry, I couldn't process that request."))
        
        print("-" * 30)

if __name__ == "__main__":
    main()