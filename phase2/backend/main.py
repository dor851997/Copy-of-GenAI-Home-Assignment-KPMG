from fastapi import FastAPI
from pydantic import BaseModel
from azure_openai import get_answer_from_openai

app = FastAPI(title="Medical Chatbot Microservice")

class ChatRequest(BaseModel):
    user_info: dict
    history: list
    question: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
async def root():
    return {"message": "Medical Chatbot backend is running."}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    answer = await get_answer_from_openai(
        question=request.question,
        user_info=request.user_info,
        history=request.history
    )

    return ChatResponse(response=answer)