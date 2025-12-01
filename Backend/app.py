from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai

genai.configure(api_key="PUT_REAL_API_KEY_HERE")

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

model = genai.GenerativeModel("models/gemini-2.5-flash")

@app.post("/chat")
def chat(req: ChatRequest):
    response = model.generate_content(req.message)
    return {"reply": response.text}
