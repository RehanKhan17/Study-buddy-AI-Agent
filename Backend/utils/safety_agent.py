import re
import google.generativeai as genai

class SafetyEscalationAgent:
    """
    V2: Hybrid Safety Detection:
    - Keyword-based HIGH-RELIABILITY detection (first)
    - LLM-based classification (fallback)
    """

    def __init__(self, model="models/gemini-2.5-flash"):
        self.model = model

        # Severe harm keywords (instant trigger)
        self.severe_keywords = [
            "kill myself", "end my life", "suicide", "i want to die",
            "i dont want to live", "i don't want to live", "hurt myself",
            "i hate living", "i want to disappear", "i wish i was dead"
        ]

        # Moderate harm keywords
        self.moderate_keywords = [
            "i feel empty", "i feel hopeless", "nothing matters",
            "i can't do this anymore", "i feel numb", "i feel worthless"
        ]

    # ------------------------------------------------------------
    # HYBRID RISK DETECTION
    # ------------------------------------------------------------

    def detect_harm_risk(self, message: str) -> dict:
        msg = message.lower().strip()

        # 1. RULE-BASED DETECTION (guaranteed)
        for phrase in self.severe_keywords:
            if phrase in msg:
                return {"risk": "severe", "reason": f"Matched severe phrase: '{phrase}'"}

        for phrase in self.moderate_keywords:
            if phrase in msg:
                return {"risk": "moderate", "reason": f"Matched moderate phrase: '{phrase}'"}

        # 2. LLM FALLBACK CLASSIFICATION
        prompt = f"""
You are a safety classifier. Analyze the message:

"{message}"

Classify strictly as one of:
- safe
- mild
- moderate
- severe

Definitions:
safe = normal irritation, academic stress
mild = sad, down, frustrated
moderate = mentions of hopelessness, giving up
severe = self-harm, suicide, desire to die, harming others

Return ONLY JSON:
{{"risk":"...","reason":"..."}}"""

        response = genai.GenerativeModel(self.model).generate_content(prompt)

        try:
            return eval(response.text)
        except:
            return {"risk": "safe", "reason": "Parsing error fallback: safe"}

    # ------------------------------------------------------------
    # ESCALATION MESSAGES
    # ------------------------------------------------------------

    def escalate_support(self, severity: str) -> str:

        if severity == "mild":
            return (
                "I'm here for you. It's okay to feel overwhelmed sometimes. "
                "You're not alone — want to talk about what's stressing you?"
            )

        if severity == "moderate":
            return (
                "It sounds like you’re going through something heavy. "
                "Talking to someone you trust can help a lot. "
                "I'm here with you — you're not alone."
            )

        if severity == "severe":
            return (
                "I'm really sorry you're feeling this way. You deserve immediate care and support.\n\n"
                "📞 **Aasra 24/7 Suicide Prevention (India): 9820466726**\n"
                "📞 **National Helpline: 9152987821**\n\n"
                "If you can, please reach out to a close friend or a family member. "
                "You are not alone, and your life matters deeply."
            )

        return ""  # safe
