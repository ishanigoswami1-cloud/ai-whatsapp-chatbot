"""
extractor.py
────────────
Uses a small, cheap LLM call to pull structured fields (name, phone, address,
city, pincode, etc.) out of the user's free-text messages and merge them into
the existing user_data dict stored in Redis.

This runs as a SEPARATE call from the main Riya conversation reply — it does
not affect what Riya says to the user. It only updates the structured data
we keep for lead generation.
"""

import json
import logging
from openai import OpenAI

log = logging.getLogger("extractor")

# Fields we ever expect to extract. Keep this in sync with what lead_api.py
# needs (see FIELD list in lead_api.py).
EXTRACTABLE_FIELDS = [
    "name",
    "phone",          # mobile number
    "email",
    "house_no",
    "area",
    "landmark",
    "city",
    "pincode",
    "state",
    "category",        # Domestic / Commercial
    "service_type",     # New Purchase / Repair / AMC / Installation etc.
    "brand",            # which brand user is interested in / chose
    "model",             # which model
    "tds",
    "budget_hint",
    "water_source",      # Municipal / Borewell / Tanker
    "company_name",       # for commercial leads
]

EXTRACTION_SYSTEM_PROMPT = f"""
You are a data-extraction assistant. You will be given:
1. The most recent user message.
2. The fields already known so far (as JSON).

Your job: extract ONLY new information present in the user's message that
matches one of these fields:
{json.dumps(EXTRACTABLE_FIELDS)}

Rules:
- Return ONLY a JSON object, nothing else. No markdown, no explanation, no backticks.
- Only include fields that are clearly and explicitly stated in the message.
- Do NOT guess, infer, or hallucinate values that are not directly stated.
- Do NOT include a field if it was already correctly captured in the known data,
  unless the user is clearly correcting/updating it.
- Phone numbers: extract digits only, no spaces or symbols (e.g. "9876543210").
- If nothing new/relevant is found, return an empty JSON object: {{}}

Example:
Known data: {{"name": "Rohit"}}
User message: "Mera number 9876543210 hai aur main Delhi mein rehta hoon"
Output: {{"phone": "9876543210", "city": "Delhi"}}
"""


def extract_fields(client: OpenAI, user_message: str, known_data: dict) -> dict:
    """
    Calls the LLM once to extract any new structured fields from user_message.
    Returns a dict of ONLY the newly found fields (empty dict if nothing found).
    Never raises — on any failure, logs and returns {} so the main chat flow
    is never blocked by extraction issues.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # cheap/fast model is enough for extraction
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Known data so far: {json.dumps(known_data, ensure_ascii=False)}\n"
                        f"User message: {user_message}"
                    ),
                },
            ],
            max_tokens=300,
            temperature=0,
        )
        raw = response.choices[0].message.content.strip()

        # Defensive cleanup in case the model wraps output in ```json fences
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:].strip()

        extracted = json.loads(raw)
        if not isinstance(extracted, dict):
            log.warning("Extractor returned non-dict JSON: %s", raw)
            return {}

        # Only keep keys we actually recognize
        extracted = {k: v for k, v in extracted.items() if k in EXTRACTABLE_FIELDS and v}
        return extracted

    except json.JSONDecodeError:
        log.warning("Extractor returned invalid JSON: %s", raw if 'raw' in locals() else "<no response>")
        return {}
    except Exception as e:
        log.error("Field extraction failed: %s", e)
        return {}