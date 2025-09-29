# src/agents/workflows/orchestrator.py
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.schemas.agent_state import AgentState
from src.agents import config
from pydantic import BaseModel, Field

class RouteQuery(BaseModel):
    route: str = Field(description="The intent keyword to route to, e.g., 'product_search', 'faq'")

prompt_path = Path(__file__).parent.parent / "prompts/orchestrator.txt"
with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_template = f.read()

def orchestrator_node(state: AgentState) -> dict:
    """Determines the user's intent and decides the route."""
    print("--- Executing Orchestrator Node ---")
    user_question = state.messages[-1].content

    llm = ChatGoogleGenerativeAI(api_key=config.GOOGLE_API_KEY, model="gemini-2.5-flash-lite").with_structured_output(RouteQuery)

    # Format the prompt and invoke the LLM
    formatted_prompt = prompt_template.format(user_question=user_question)
    response = llm.invoke(formatted_prompt)

    print(f"Intent determined: {response.route}")
    return {"route": response.route}