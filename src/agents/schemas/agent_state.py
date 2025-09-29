from pydantic import BaseModel, Field
from typing import List, Optional, Any
from langchain_core.messages import BaseMessage
from src.agents.schemas.evaluator_schemas import ResultReview

class AgentState(BaseModel):
    messages: List[BaseMessage]
    search_results: Optional[list[dict]] = None
    route: Optional[str] = None
    filtered_results: Optional[list[dict]] = None
    result_review: Optional[ResultReview] = None
    retries: int = 0
    prior_conversation: str = ""