import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import RiyaChatbot

app = Flask(__name__)
CORS(app)

bot = RiyaChatbot()

log = logging.getLogger("app")

# ── Chat ──────────────────────────────────────
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        log.warning("POST /chat → 400 Bad Request (message field missing)")
        return jsonify({"error": "message field required"}), 400

    session_id = data.get("session_id") or f"session_{uuid.uuid4().hex[:8]}"
    message    = data["message"].strip()

    if not message:
        log.warning("[%s] POST /chat → 400 Bad Request (empty message)", session_id)
        return jsonify({"error": "Empty message"}), 400

    log.info("[%s] ──────── New /chat request ────────", session_id)
    try:
        reply = bot.chat(session_id, message)
        log.info("[%s] POST /chat → 200 OK", session_id)
        return jsonify({"session_id": session_id, "reply": reply})
    except Exception as e:
        log.exception("[%s] POST /chat → 500 Internal Server Error", session_id)
        return jsonify({"error": str(e)}), 500

# ── New Session (auto greet) ──────────────────
@app.route("/new-session", methods=["POST"])
def new_session():
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    log.info("[%s] ──────── New session started ────────", session_id)
    opening    = bot.chat(session_id, "Hello")
    log.info("[%s] POST /new-session → 200 OK", session_id)
    return jsonify({"session_id": session_id, "reply": opening})

# ── Leads (admin only) ────────────────────────
@app.route("/leads", methods=["GET"])
def get_leads():
    # TODO: Production mein jaane se pehle authentication add karo!
    leads = bot.memory.get_all_leads()
    log.info("GET /leads → 200 OK (total=%d)", len(leads))
    return jsonify({"total": len(leads), "leads": leads})

if __name__ == "__main__":
    app.run(debug=True, port=5000)