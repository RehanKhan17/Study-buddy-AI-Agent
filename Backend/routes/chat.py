from utils.study_agent import StudyAgent
from utils.safety_agent import SafetyAgent
from flask import Blueprint, request, jsonify
from utils.gemini_client import generate_with_gemini

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.json.get("message", "")

        if not user_input:
            return jsonify({"error": "Message is required"}), 400

        response = generate_with_gemini(user_input)

        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
