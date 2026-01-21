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
