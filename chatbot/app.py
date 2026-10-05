import os
import sqlite3
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from chatbot_config import SYSTEM_PROMPT, CHATBOT_TITLE, QUICK_QUESTIONS, init_database, search_products

load_dotenv()

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

client = genai.Client(api_key=API_KEY) if API_KEY else None

init_database()


def ask_gemini(user_message):
    if not client:
        return "Gemini API key is not configured. Please add GEMINI_API_KEY to the .env file."

    products = search_products(user_message)

    product_context = ""
    if products:
        product_context = "\n\nRelevant Glowora product knowledge:\n" + "\n".join(
            f"- {p['name']} | Category: {p['category']} | Skin type: {p['skin_type']} | "
            f"Ingredients: {p['ingredients']} | {p['description']}"
            for p in products
        )

    prompt = f"""{SYSTEM_PROMPT}

User question:
{user_message}

{product_context}

Answer the user according to the Glowora AI rules. Keep the response useful and concise.
Do not claim that a sample database product is a real commercially available product.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text.strip() if response.text else "I couldn't generate a response right now."
    except Exception as exc:
        return f"Sorry, I couldn't connect to the AI service right now. ({type(exc).__name__})"


@app.route("/")
def index():
    return render_template(
        "index.html",
        chatbot_title=CHATBOT_TITLE,
        quick_questions=QUICK_QUESTIONS
    )


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"reply": "Please enter a skincare or beauty question."}), 400

    reply = ask_gemini(message)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
