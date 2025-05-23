from fastapi import APIRouter
from models.chat import ChatRequest, ChatResponse
from agent.weather_agent import get_agent_response

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    reply = get_agent_response(req.query, req.session_id)
    return ChatResponse(response=reply)