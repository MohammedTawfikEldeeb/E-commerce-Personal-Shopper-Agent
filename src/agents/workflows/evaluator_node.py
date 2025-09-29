from src.agents.schemas.agent_state import AgentState 
from src.agents.schemas.evaluator_schemas import ResultReview
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage
from src.agents import config
from pathlib import Path

evaluator_prompt_path = Path(__file__).parent.parent / "prompts/evaluator.txt"
with open(evaluator_prompt_path, 'r', encoding='utf-8') as f: 
    evaluator_prompt_template = f.read()

def evaluator_node(state: AgentState):
    """
    Evaluates search results using an LLM to see if they match the user's query,
    considering the prior conversation.
    """
    print("--- Executing Intelligent Evaluator Node ---")
    user_query = state.messages[-1].content
    search_results = state.search_results
    prior_conversation = getattr(state, "prior_conversation", "")

    if not search_results:
        review = ResultReview(is_valid=False)
        return {
            "result_review": review, 
            "filtered_results": [], 
            "retries": state.retries + 1
        }
    
    try:
        # Evaluate all search results
        formatted_prompt = evaluator_prompt_template.format(
            user_query=user_query,
            prior_conversation=prior_conversation,
            search_results=str(search_results[:10])  # Limit to first 10 results
        )

        llm = ChatGoogleGenerativeAI(
            api_key=config.GOOGLE_API_KEY, 
            model="gemini-2.5-flash-lite"
        ).with_structured_output(ResultReview)

        review = llm.invoke(formatted_prompt)
        print(f"Evaluation result: is_valid = {review.is_valid}")

        # If evaluation passes, send all results to generator
        # If evaluation fails, send empty list
        filtered_results = search_results if review.is_valid else []
        return {
            "result_review": review.model_dump(), 
            "filtered_results": filtered_results,
            "retries": state.retries + 1
        }
    except Exception as e:
        print(f"Error in evaluator node: {e}")
        # In case of error, be conservative and don't show any results
        return {
            "result_review": ResultReview(is_valid=False, reasoning=f"Error during evaluation: {str(e)}").model_dump(),
            "filtered_results": [],
            "retries": state.retries + 1
        }