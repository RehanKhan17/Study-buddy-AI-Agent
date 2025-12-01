from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# ------------------ CONFIG ------------------
genai.configure(api_key="PUT_REAL_API_KEY_HERE")   

model = genai.GenerativeModel("gemini-2.5-flash")

# ------------------ FASTAPI APP ------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],   # FIXED HERE
    allow_headers=["*"],
)

# ------------------ REQUEST MODEL ------------------
class ChatRequest(BaseModel):
    message: str


# ------------------ ROUTES ------------------

@app.get("/")
def home():
    return {"message": "Backend running successfully!"}


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        response = model.generate_content(req.message)
        return {"reply": response.text}
    except Exception as e:
        return {"error": str(e)}


# ------------------ RUN ------------------
# run command:
# uvicorn main:app --reload
