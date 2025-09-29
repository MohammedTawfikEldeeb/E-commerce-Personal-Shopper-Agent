from src.agents.schemas.agent_state import AgentState 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage
from src.agents import config
from pathlib import Path

generator_prompt_path = Path(__file__).parent.parent / "prompts/generator.txt"
with open(generator_prompt_path, 'r', encoding='utf-8') as f: 
    generator_prompt_template = f.read()

faq_generator_prompt_path = Path(__file__).parent.parent / "prompts/faq_generator.txt"
with open(faq_generator_prompt_path, 'r', encoding='utf-8') as f: 
    faq_generator_prompt_template = f.read()

def generative_node(state: AgentState) -> dict:
    print("--- Executing Generative Node ---")

    user_query = state.messages[-1].content
    filtered_results = state.filtered_results
    route = getattr(state, "route", "product_search")  # Default to product search

    if route == "faq":
        # Handle FAQ generation
        faq_list_str = ""
        if not filtered_results:
            faq_list_str = "No relevant FAQ information found."
        else:
            # Format FAQ results
            for i, faq in enumerate(filtered_results):
                faq_list_str += f"{faq['content']}\n\n"

        llm = ChatGoogleGenerativeAI(
            api_key=config.GOOGLE_API_KEY, 
            model="gemini-2.5-flash-lite"
        )

        formatted_prompt = faq_generator_prompt_template.format(
            user_query=user_query,
            faq_list=faq_list_str,
            prior_conversation=state.prior_conversation
        )

        final_response_text = llm.invoke(formatted_prompt).content
    else:
        # Handle product search generation (existing logic)
        product_list_str = ""
        if not filtered_results:
            product_list_str = "No products found."
        else:
            # Include all filtered products in the prompt so the AI can choose which to mention
            for i, product in enumerate(filtered_results):
                meta = product.get('metadata', {})
                title = meta.get('title', 'N/A')
                price = meta.get('sale_price', 'N/A')
                currency = meta.get('currency', '') 
                product_list_str += f"{i+1}. Title: {title}, Price: {currency} {price}\n"

        llm = ChatGoogleGenerativeAI(
            api_key=config.GOOGLE_API_KEY, 
            model="gemini-2.5-flash-lite"
        )

        formatted_prompt = generator_prompt_template.format(
            user_query=user_query,
            product_list=product_list_str,
            prior_conversation=state.prior_conversation
        )

        final_response_text = llm.invoke(formatted_prompt).content

    # Only append the AI message - memory update will be handled separately
    messages = state.messages + [AIMessage(content=final_response_text)]

    return {
        "messages": messages
        # Don't update prior_conversation here - let update_memory handle it
    }