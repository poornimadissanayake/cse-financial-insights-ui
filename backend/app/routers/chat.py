from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm_service import get_llm_response
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await get_llm_response(request.message)
        if not response:
            raise HTTPException(status_code=500, detail="Failed to generate response")
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 