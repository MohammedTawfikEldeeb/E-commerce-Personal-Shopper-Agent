from langgraph.graph import StateGraph, END
from src.agents.schemas.agent_state import AgentState
from src.agents.workflows.orchestrator import orchestrator_node
from src.agents.workflows.search_node import search_node
from src.agents.workflows.evaluator_node import evaluator_node
from src.agents.workflows.generator_node import generative_node
from src.agents.workflows.faq_workflow import faq_node
from src.agents.workflows.working_memory import load_conversation_memory, update_conversation_memory
from langchain_core.messages import AIMessage, HumanMessage


def route_logic(state: AgentState) -> str:
    """
    Determines the next step based on the identified user intent.
    """
    route = state.route
    if route == 'product_search':
        return "search"
    elif route == 'faq':
        return "faq"
    else:
        return END


MAX_RETRIES = 2

def decide_after_evaluation(state: AgentState) -> str:

    if state.result_review and state.result_review.is_valid:
        print("--- Decision: Results are valid. Proceeding to generate response. ---")
        return "generate"
    elif state.retries >= MAX_RETRIES:
        print(f"--- Decision: Max retries ({MAX_RETRIES}) reached. Proceeding to generate failure response. ---")
        return "generate"
    else:
        print(f"--- Decision: Results are invalid (Attempt {state.retries}). Looping back to search. ---")
        return "search"


workflow = StateGraph(AgentState)

# Nodes
workflow.add_node("load_memory", load_conversation_memory)  # Load memory at start
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("search", search_node)
workflow.add_node("evaluator", evaluator_node)
workflow.add_node("generator", generative_node)
workflow.add_node("faq", faq_node)
workflow.add_node("update_memory", update_conversation_memory)  # Update memory at end

workflow.set_entry_point("load_memory")

workflow.add_edge("load_memory", "orchestrator")

workflow.add_conditional_edges(
    "orchestrator",
    route_logic,
    {
        "search": "search",
        "faq": "faq",
        END: END
    }
)

workflow.add_edge("search", "evaluator")

workflow.add_conditional_edges(
    "evaluator",
    decide_after_evaluation,
    {
        "generate": "generator",
        "search": "search",
    }
)

workflow.add_edge("generator", "update_memory")
workflow.add_edge("faq", "generator")

workflow.add_edge("update_memory", END)

app = workflow.compile()
mermaid_string = app.get_graph().draw_mermaid()

with open("workflow_graph.md", "w", encoding="utf-8") as f:
    f.write(f"```mermaid\n{mermaid_string}\n```")

print("Graph definition saved to workflow_graph.md")

state = {"messages": []}  
