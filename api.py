from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from src.agents.graph import app as agent_app
from langchain_core.messages import HumanMessage, AIMessage
import asyncio
import uuid
import json
import re

# Create FastAPI app instance
api = FastAPI(title="E-commerce Personal Shopper Agent API",
              description="API for the E-commerce Personal Shopper Agent using RAG pipeline",
              version="1.0.0")

# Add CORS middleware to allow frontend connections
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for conversation sessions
conversation_sessions = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    products: Optional[List[Dict]] = None

class HealthCheckResponse(BaseModel):
    status: str
    message: str

@api.get("/", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint to verify API is running"""
    return HealthCheckResponse(
        status="healthy",
        message="E-commerce Personal Shopper Agent API is running"
    )

@api.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Endpoint for chatting with the e-commerce agent"""
    try:
        if req.session_id:
            session_id = req.session_id
        else:
            session_id = str(uuid.uuid4())
        
        if session_id not in conversation_sessions:
            conversation_sessions[session_id] = []
        
        conversation_history = conversation_sessions[session_id]
        conversation_history.append(HumanMessage(content=req.message))
        
        inputs = {"messages": conversation_history}
        
        response = agent_app.invoke(inputs)
        
        updated_history = response.get("messages", [])
        conversation_sessions[session_id] = updated_history
        
        ai_response = "Sorry, I couldn't process that request."
        if updated_history and isinstance(updated_history[-1], AIMessage):
            ai_response = updated_history[-1].content
        elif "search_results" in response:
            # Fallback for workflows that don't add an AIMessage
            ai_response = str(response.get("search_results", ai_response))
        
        route = response.get("route", "")
        
        products_to_return = None
        if route != "faq":
            filtered_products = response.get("filtered_results", [])
            
            mentioned_products = extract_mentioned_products(ai_response, filtered_products)
            products_to_return = mentioned_products
        
        return ChatResponse(response=ai_response, session_id=session_id, products=products_to_return)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

def extract_mentioned_products(response_text: str, filtered_products: List[Dict]) -> List[Dict]:
    """
    Extract products that are actually mentioned in the AI response.
    This is a simple implementation that looks for product titles in the response.
    """
    if not filtered_products:
        return []
    
    mentioned_products = []
    
    for product in filtered_products:
        meta = product.get('metadata', {})
        title = meta.get('title', '').lower()
        
        if title and title in response_text.lower():
            mentioned_products.append(product)
    

    if not mentioned_products and filtered_products:
        return filtered_products
    
    return mentioned_products

@api.get("/sessions/{session_id}")
async def get_session_history(session_id: str):
    """Get the conversation history for a specific session"""
    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    history = conversation_sessions[session_id]
    formatted_history = []
    
    for msg in history:
        if isinstance(msg, HumanMessage):
            formatted_history.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            formatted_history.append({"role": "assistant", "content": msg.content})
    
    return {"session_id": session_id, "history": formatted_history}

@api.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear the conversation history for a specific session"""
    if session_id in conversation_sessions:
        del conversation_sessions[session_id]
        return {"message": f"Session {session_id} cleared"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@api.get("/sessions")
async def list_sessions():
    """List all active session IDs"""
    return {"sessions": list(conversation_sessions.keys())}