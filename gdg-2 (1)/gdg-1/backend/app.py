from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/api/verify", methods=["POST"])
def verify_internship():
    data = request.json

    company = data.get("company", "").lower()
    domain = data.get("domain", "").lower()
    message = data.get("message", "").lower()

    score = 0
    reasons = []

    # ---------- RULE 1: Scam / Payment Keywords ----------
    scam_keywords = [
        "fee", "fees", "pay", "payment", "registration",
        "processing", "urgent", "limited slots",
        "confirm now", "today only"
    ]

    if any(word in message for word in scam_keywords):
        score += 40
        reasons.append("Payment or urgency related keywords detected")

    # ---------- RULE 2: Free Email Domains ----------
    free_email_domains = ["gmail", "yahoo", "outlook", "hotmail"]

    if any(mail in domain for mail in free_email_domains):
        score += 30
        reasons.append("Uses free/public email domain instead of official company domain")

    # ---------- RULE 3: Missing or Invalid Domain ----------
    if domain.strip() == "":
        score += 20
        reasons.append("No official company domain provided")

    # ---------- RULE 4: Brand Name Misuse (Basic Check) ----------
    known_brands = ["google", "microsoft", "amazon", "infosys", "tcs"]

    if any(brand in message and brand not in domain for brand in known_brands):
        score += 30
        reasons.append("Possible misuse of well-known company name")

    # ---------- FINAL VERDICT ----------
    if score >= 60:
        verdict = "Likely Scam"
    elif score >= 30:
        verdict = "Suspicious"
    else:
        verdict = "Looks Legit"

    return jsonify({
        "company": company,
        "risk_score": score,
        "verdict": verdict,
        "reasons": reasons
    })


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "InternShield Backend is running"
    })


if __name__ == "__main__":
    app.run(debug=True)



'''

from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
import os

# ------------------ CONFIG ------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY environment variable not set")

client = genai.Client(api_key=GEMINI_API_KEY)

# ------------------ APP SETUP ------------------
app = Flask(__name__)
CORS(app)

# ------------------ AI FUNCTION ------------------
def ai_scam_check(message, domain):
    prompt = f"""
You are a cybersecurity assistant helping students avoid internship scams.

Analyze the following internship message and domain.
Respond ONLY in valid JSON format:
{{
  "ai_verdict": "Legit or Scam",
  "ai_reason": "Short explanation"
}}

Domain: {domain}
Message:
{message}
"""
    try:
        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return '{"ai_verdict": "Unknown", "ai_reason": "AI service unavailable"}'

# ------------------ API ROUTE ------------------
@app.route("/api/verify", methods=["POST"])
def verify_internship():
    data = request.json

    company = data.get("company", "").lower()
    domain = data.get("domain", "").lower()
    message = data.get("message", "").lower()

    score = 0
    reasons = []

    # ---------- RULE ENGINE ----------
    scam_keywords = [
        "fee", "fees", "pay", "payment", "registration",
        "processing", "urgent", "limited slots",
        "confirm now", "today only"
    ]

    if any(word in message for word in scam_keywords):
        score += 40
        reasons.append("Payment or urgency related keywords detected")

    free_email_domains = ["gmail", "yahoo", "outlook", "hotmail"]

    if any(mail in domain for mail in free_email_domains):
        score += 30
        reasons.append("Uses free/public email domain instead of official company domain")

    if domain.strip() == "":
        score += 20
        reasons.append("No official company domain provided")

    known_brands = ["google", "microsoft", "amazon", "infosys", "tcs"]

    if any(brand in message and brand not in domain for brand in known_brands):
        score += 30
        reasons.append("Possible misuse of well-known company name")

    # ---------- RULE VERDICT ----------
    if score >= 60:
        verdict = "Likely Scam"
    elif score >= 30:
        verdict = "Suspicious"
    else:
        verdict = "Looks Legit"

    # ---------- AI VALIDATION ----------
    ai_result = ai_scam_check(message, domain)
    reasons.append("AI Validation (Google Gemini): " + ai_result)

    return jsonify({
        "company": company,
        "risk_score": score,
        "verdict": verdict,
        "reasons": reasons
    })

# ------------------ HEALTH CHECK ------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "InternShield Backend with Google Gemini (GenAI SDK) is running"
    })

# ------------------ RUN SERVER ------------------
if __name__ == "__main__":
    app.run(debug=True)



'''
