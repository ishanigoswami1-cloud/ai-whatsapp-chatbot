"""
lead_api.py
────────────
Sends a collected lead to the CRM endpoint:
https://inet.waterpurifierservicecenter.in/chatbot_rocare.php

Confirmed via testing:
- Endpoint accepts POST with FORM-ENCODED data only (requests.post(url, data=...))
  - POST JSON -> fails ("Session ID or Mobile required")
  - GET query params -> fails ("Session ID or Mobile required")
- mobile and session_id are required on every call.
- Successful response looks like:
  {"status": true, "chat_id": 16035, "session_id": "...", "message": "Data saved successfully", "transferred": false}
- NOTE: "transferred": false in the response is still unconfirmed in meaning —
  follow up with your team on whether an extra field/status is needed to make
  the lead show up as "transferred" in the actual CRM dashboard.
"""

import logging
import requests

log = logging.getLogger("lead-api")

LEAD_API_URL = "https://inet.waterpurifierservicecenter.in/chatbot_rocare.php"


def map_user_data_to_lead_payload(session_id: str, user_data: dict, chat_text: str = "") -> dict:
    """
    Converts this project's user_data dict (as stored in Redis via memory.py)
    into the exact field names the CRM API expects.
    """
    payload = {
        "session_id": session_id,
        "mobile": user_data.get("phone", ""),
        "name": user_data.get("name", ""),
        "email": user_data.get("email", ""),
        "pincode": user_data.get("pincode", ""),
        "state": user_data.get("state", ""),
        "city": user_data.get("city", ""),
        "category": user_data.get("category", ""),          # Domestic / Commercial
        "service_type": user_data.get("service_type", ""),   # New Purchase / Repair / AMC etc.
        "brand": user_data.get("brand", ""),
        "model": user_data.get("model", ""),
        "preferred_date": user_data.get("preferred_date", ""),
        "time_slot": user_data.get("time_slot", ""),
        "last_service_date": user_data.get("last_service_date", ""),
        "problem_description": user_data.get("problem_description", ""),
        "house_no": user_data.get("house_no", ""),
        "area": user_data.get("area", ""),
        "landmark": user_data.get("landmark", ""),
        "status": "New_purchase",
        "serviceprice": user_data.get("serviceprice", ""),
        "source": "ROCare_sales_chatbot",
        "complain_type": user_data.get("complain_type", ""),
        "city_id": user_data.get("city_id", ""),
        "img_url": user_data.get("img_url", ""),
        "location_maps_link": user_data.get("location_maps_link", ""),
        "location_lat": user_data.get("location_lat", ""),
        "location_lng": user_data.get("location_lng", ""),
        "chat": chat_text,
    }
    return payload


def send_lead_to_crm(session_id: str, user_data: dict, chat_text: str = "") -> dict:
    """
    Sends the lead to the CRM API. Returns:
    {"success": True/False, "response": {...} or raw text, "error": "..." or None}
    """
    payload = map_user_data_to_lead_payload(session_id, user_data, chat_text)

    if not payload["mobile"]:
        log.warning("Refusing to send lead — mobile number missing. session_id=%s", session_id)
        return {"success": False, "response": None, "error": "mobile number missing"}

    log.info("→ Calling CRM Lead API | url=%s | session_id=%s | mobile=%s***",
             LEAD_API_URL, session_id, payload["mobile"][:5] if payload["mobile"] else "")

    try:
        response = requests.post(LEAD_API_URL, data=payload, timeout=10)
    except requests.RequestException as e:
        log.error("Lead API request failed: %s", e)
        return {"success": False, "response": None, "error": str(e)}

    log.info("← CRM Lead API responded | status_code=%s", response.status_code)

    if response.status_code != 200:
        log.error("Lead API returned non-200: %s %s", response.status_code, response.text)
        return {"success": False, "response": response.text, "error": f"HTTP {response.status_code}"}

    try:
        data = response.json()
    except ValueError:
        log.error("Lead API returned non-JSON response: %s", response.text)
        return {"success": False, "response": response.text, "error": "invalid JSON response"}

    if data.get("status") is True:
        log.info("Lead sent successfully. chat_id=%s session_id=%s", data.get("chat_id"), session_id)
        return {"success": True, "response": data, "error": None}
    else:
        log.warning("Lead API rejected the lead: %s", data)
        return {"success": False, "response": data, "error": data.get("message", "unknown error")}