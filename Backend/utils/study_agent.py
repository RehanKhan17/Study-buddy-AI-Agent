import os
from dotenv import load_dotenv
import google.generativeai as genai
from safety_agent import SafetyEscalationAgent

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=API_KEY)


class StudyBuddyChatbot:
    """
    Study Buddy with integrated Safety Agent (V2).
    """

    def __init__(self, model="models/gemini-2.5-flash"):
        self.model = model
        self.chat_history = []
        self.safety_agent = SafetyEscalationAgent(model=model)

    # ------------------------------------------------------------
    # BUILD PROMPT
    # ------------------------------------------------------------

    def _build_prompt(self, user_message: str) -> str:

        history = ""
        for turn in self.chat_history:
            history += f"User: {turn['user']}\nBuddy: {turn['bot']}\n"

        prompt = f"""
You are STUDY BUDDY — a friendly, warm educational chatbot.

You should:
- Answer any study question simply & kindly
- Be conversational & supportive
- Use memory for context
- NEVER solve exam/homework directly (explain concepts instead)
- Encourage the student like a real buddy

Chat history:
{history}

User: {user_message}

Reply as a friendly study buddy.
"""

        return prompt

    # ------------------------------------------------------------
    # MAIN CHAT HANDLER
    # ------------------------------------------------------------

    def chat(self, user_message: str) -> str:

        # -------------- SAFETY CHECK FIRST --------------
        risk_info = self.safety_agent.detect_harm_risk(user_message)
        risk = risk_info["risk"]

        print(f"[DEBUG] Risk detection:", risk_info)  # <<-- Keep this line

        if risk != "safe":
            escalation_msg = self.safety_agent.escalate_support(risk)

            # Save memory
            self.chat_history.append({
                "user": user_message,
                "bot": escalation_msg
            })

            return escalation_msg

        # -------------- NORMAL CHAT --------------
        prompt = self._build_prompt(user_message)
        response = genai.GenerativeModel(self.model).generate_content(prompt)

        bot_reply = response.text.strip()

        # Store memory
        self.chat_history.append({
            "user": user_message,
            "bot": bot_reply
        })

        # limit memory
        self.chat_history = self.chat_history[-10:]

        return bot_reply


# ------------------------------------------------------------
# RUN CHATBOT LOOP
# ------------------------------------------------------------

if __name__ == "__main__":
    bot = StudyBuddyChatbot()

    print("Welcome to Study Buddy, how can I help you?\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Buddy: Take care bro! See you soon 😊")
            break

        reply = bot.chat(user_input)
        print("Buddy:", reply, "\n")
