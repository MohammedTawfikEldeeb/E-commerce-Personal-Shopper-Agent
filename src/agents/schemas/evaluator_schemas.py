from pydantic import BaseModel, Field
from typing import Optional

class ResultReview(BaseModel):
    """Defines the structured output for the evaluator's review decision."""
    is_valid: bool = Field(description="Whether the search results meet the customer's requirements.")
    reasoning: str = Field(description="A brief explanation for the is_valid decision.")