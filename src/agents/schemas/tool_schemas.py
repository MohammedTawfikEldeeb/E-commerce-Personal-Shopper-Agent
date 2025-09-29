from pydantic import BaseModel, Field

class ProductSearchInput(BaseModel):
    query: str = Field(description="The user's search query for a product.")
    conversation_history: str = Field(default="", description="The conversation history for context awareness.")


class FAQSearchInput(BaseModel):
    query: str = Field(description="The user's FAQ query.")