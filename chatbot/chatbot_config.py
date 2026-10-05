import sqlite3
import re

CHATBOT_TITLE = "Glowora AI"

QUICK_QUESTIONS = [
    "Recommend a moisturizer for oily skin",
    "What ingredients help dry skin?",
    "Give me a simple skincare routine",
    "Explain niacinamide",
    "How should I use sunscreen?",
    "Give me hair-care tips",
    "Give me lip-care tips",
    "Give me nail-care tips",
    "Give me body-care tips",
]

SYSTEM_PROMPT = """
You are Glowora AI, a focused AI beauty and personal-care assistant.

Your ONLY purpose is to answer questions related to:
1. Skin types and basic skincare
2. Skin-type based product recommendations
3. Beauty product categories
4. Skincare ingredients and their general cosmetic uses
5. Sunscreen and sun-protection guidance
6. Basic skincare routines
7. Hair-care
8. Lip-care
9. Nail-care
10. Body-care
11. General beauty and personal-care education

Behavior rules:
- Stay strictly within the Glowora beauty/personal-care scope.
- If a question is unrelated to beauty, skincare, hair-care, lip-care, nail-care, body-care, products, ingredients, or personal-care routines, politely refuse and redirect the user to Glowora topics.
- Do not answer unrelated coding, politics, entertainment, homework, finance, sports, general knowledge, or other off-topic questions.
- Give practical, easy-to-understand answers.
- Do not diagnose medical conditions.
- For serious, persistent, painful, allergic, or rapidly changing skin/hair/nail concerns, recommend consulting a qualified healthcare professional.
- Do not promise that a product will cure a disease or guarantee a result.
- When recommending products, consider skin type, concern, ingredients, and product category.
- Explain that product recommendations in the local database are sample Glowora products, not claims about real-world commercial availability.
- Avoid making unsupported claims about brands or clinical results.
- Ask a short follow-up question when the user's request lacks the skin type, concern, or product category needed for a useful recommendation.
- Keep answers concise but helpful.
- Use clear headings or bullets when useful.
"""

DB_PATH = "glowora.db"

PRODUCTS = [
    ("Hydra Glow Moisturizer", "Moisturizer", "dry,normal",
     "dryness", "hyaluronic acid, ceramides",
     "A sample hydrating moisturizer concept for dry and normal skin."),
    ("Oil Balance Gel", "Moisturizer", "oily,combination",
     "oiliness", "niacinamide, aloe vera",
     "A sample lightweight gel moisturizer concept for oily and combination skin."),
    ("Clear Skin Cleanser", "Cleanser", "oily,combination",
     "oiliness,blemish-prone skin", "salicylic acid, niacinamide",
     "A sample cleanser concept for oily and combination skin."),
    ("Soft Barrier Cleanser", "Cleanser", "dry,sensitive",
     "dryness,sensitivity", "ceramides, aloe vera",
     "A sample gentle cleanser concept for dry and sensitive skin."),
    ("Daily Shield SPF 50", "Sunscreen", "all",
     "sun protection", "zinc oxide, aloe vera",
     "A sample daily sunscreen concept for exposed skin."),
    ("Glow Renewal Serum", "Serum", "normal,combination",
     "dull-looking skin", "niacinamide, glycolic acid",
     "A sample brightening serum concept."),
    ("Hydra Boost Serum", "Serum", "dry,normal",
     "dryness", "hyaluronic acid, peptides",
     "A sample hydrating serum concept."),
]


def init_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            skin_type TEXT NOT NULL,
            concerns TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)
    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
            INSERT INTO products
            (name, category, skin_type, concerns, ingredients, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, PRODUCTS)
    conn.commit()
    conn.close()


def search_products(query):
    text = query.lower()
    skin_types = ["oily", "dry", "combination", "sensitive", "normal"]
    categories = ["moisturizer", "cleanser", "sunscreen", "serum"]

    selected_skin = next((x for x in skin_types if x in text), None)
    selected_category = next((x for x in categories if x in text), None)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    sql = "SELECT * FROM products WHERE 1=1"
    params = []

    if selected_category:
        sql += " AND category = ?"
        params.append(selected_category.title())

    if selected_skin:
        sql += " AND (skin_type LIKE ? OR skin_type = 'all')"
        params.append(f"%{selected_skin}%")

    sql += " LIMIT 4"
    cur.execute(sql, params)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows
