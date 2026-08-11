import logging
from datetime import datetime
from openai import OpenAI
from product import get_products
from prompt import build_system_prompt
from memory import RedisMemory
from exractor import extract_fields
from lead  import send_lead_to_crm
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

log = logging.getLogger("riya-chatbot")

# This must match exactly what the system prompt's Final Lead Summary
# section outputs (see prompt.py, Final Lead Summary: "Lead Status: New_purchase").
# FIXED: previously this said "ROCare_sales_chatbot" which never appeared in
# Riya's actual reply, so leads were never detected/pushed to CRM.
LEAD_TRIGGER_MARKER = "Lead Status: New_Purchase"


def mobile_to_session_id(mobile_number: str) -> str:
    """
    Converts any raw mobile number format into a consistent session_id,
    so the same customer always lands in the same session regardless of
    how their number was typed/sent (with/without +91, spaces, dashes).

    Examples, all produce the same session_id:
      "+91 99999 99999"  -> "919999999999"
      "91-9999999999"    -> "919999999999"
      "9999999999"       -> "919999999999"   (assumes Indian number, adds 91 prefix)
    """
    digits = "".join(ch for ch in mobile_number if ch.isdigit())

    # Normalize to include country code "91" once, drop any leading 0
    digits = digits.lstrip("0")
    if len(digits) == 10:
        digits = "91" + digits
    elif digits.startswith("0091"):
        digits = digits[2:]
    elif digits.startswith("091"):
        digits = digits[1:]

    return digits


class RiyaChatbot:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.memory = RedisMemory()

    def chat(self, session_id: str, user_message: str) -> str:
        history = self.memory.get_history(session_id)
        user_data = self.memory.get_user_data(session_id)

        # session_id is expected to be the customer's mobile number
        # (see mobile_to_session_id() above — call that BEFORE calling chat()).
        # Auto-fill phone in user_data if not already set, so it's never
        # missing for lead generation even if the LLM extractor misses it.
        if not user_data.get("phone"):
            user_data["phone"] = session_id

        history.append({"role": "user", "content": user_message})

        log.info("[%s] → Fetching product catalog (Doctor Fresh API + static brands)...", session_id)
        products = get_products()
        log.info("[%s] ✓ Got %d products", session_id, len(products))

        system_prompt = build_system_prompt(products, user_data)

        # ── Main Riya reply (conversation-facing call) ──────────────────────
        log.info("[%s] → Calling OpenAI gpt-4o for Riya's reply...", session_id)
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                *history
            ],
            max_tokens=1000,
            temperature=0.7
        )
        log.info("[%s] ✓ OpenAI gpt-4o reply received", session_id)

        assistant_message = response.choices[0].message.content

        history.append({"role": "assistant", "content": assistant_message})
        self.memory.save_history(session_id, history)
        log.info("[%s] ✓ History saved to Redis", session_id)

        # ── Structured field extraction (separate, silent LLM call) ────────
        # This does NOT affect what Riya says — it only updates user_data
        # so name/phone/address/etc. are reliably captured for lead generation.
        log.info("[%s] → Calling OpenAI gpt-4o-mini for field extraction...", session_id)
        newly_extracted = extract_fields(self.client, user_message, user_data)
        log.info("[%s] ✓ Extraction done", session_id)
        if newly_extracted:
            log.info("Extracted new fields for session %s: %s", session_id, newly_extracted)

        updated_data = {**user_data, **newly_extracted}
        self.memory.save_user_data(session_id, updated_data)
        log.info("[%s] ✓ User data saved to Redis", session_id)

        # ── Lead detection + CRM push ────────────────────────────────────────
        self._check_and_save_lead(session_id, assistant_message, updated_data, history)

        return assistant_message

    def _check_and_save_lead(self, session_id: str, reply: str, user_data: dict, history: list):
        """
        Triggers when Riya's reply contains the Final Lead Summary marker
        (see prompt.py Section 14). Saves the lead locally in Redis AND
        pushes it to the CRM via lead_api.py. Won't double-send if the
        lead was already pushed in this session.
        """
        if LEAD_TRIGGER_MARKER not in reply:
            return

        log.info("[%s] 🎯 Lead marker detected in Riya's reply!", session_id)

        if user_data.get("lead_sent"):
            log.info("Lead already sent for session %s — skipping duplicate push.", session_id)
            return

        # Save a local record in Redis (existing behavior, kept for your records)
        lead = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "collected_user_data": user_data,
        }
        lead_id = self.memory.save_lead(lead)
        log.info("[%s] 📋 Lead saved locally in Redis: %s", session_id, lead_id)

        # Push to CRM
        chat_text = "\n".join(f"{turn['role']}: {turn['content']}" for turn in history)
        log.info("[%s] → Pushing lead to CRM API...", session_id)
        result = send_lead_to_crm(session_id, user_data, chat_text)

        if result["success"]:
            log.info("[%s] ✅ Lead pushed to CRM. chat_id=%s", session_id, result["response"].get("chat_id"))
            user_data["lead_sent"] = True
            self.memory.save_user_data(session_id, user_data)
        else:
            log.error("[%s] ❌ Lead push to CRM failed: %s", session_id, result["error"])
            # Lead is still saved locally (lead_id above) even if CRM push fails,
            # so nothing is lost — you can retry/inspect it later via get_all_leads().