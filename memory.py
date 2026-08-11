import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

try:
    from upstash_redis import Redis
    _client = Redis(
        url=os.getenv("UPSTASH_REDIS_REST_URL"),
        token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
    )
    _client.ping()
    REDIS_AVAILABLE = True
    print("✅ Redis connected")
except Exception as e:
    print(f"⚠️  Redis unavailable, using in-memory fallback: {e}")
    REDIS_AVAILABLE = False
    _client = None

SESSION_EXPIRY = 60 * 60 * 24  # 24 hours


class RedisMemory:
    def __init__(self):
        self.client = _client if REDIS_AVAILABLE else None
        self._fallback = {}

    def _key(self, session_id, suffix):
        return f"ro_care:{session_id}:{suffix}"

    # ── Conversation History ──────────────────────────────────────────────────

    def get_history(self, session_id: str) -> list:
        if self.client:
            data = self.client.get(self._key(session_id, "history"))
            return json.loads(data) if data else []
        return self._fallback.get(f"{session_id}:history", [])

    def save_history(self, session_id: str, history: list):
        if self.client:
            self.client.setex(
                self._key(session_id, "history"),
                SESSION_EXPIRY,
                json.dumps(history)
            )
        else:
            self._fallback[f"{session_id}:history"] = history

    # ── User Data ─────────────────────────────────────────────────────────────

    def get_user_data(self, session_id: str) -> dict:
        if self.client:
            data = self.client.get(self._key(session_id, "user_data"))
            return json.loads(data) if data else {}
        return self._fallback.get(f"{session_id}:user_data", {})

    def save_user_data(self, session_id: str, data: dict):
        if self.client:
            self.client.setex(
                self._key(session_id, "user_data"),
                SESSION_EXPIRY,
                json.dumps(data)
            )
        else:
            self._fallback[f"{session_id}:user_data"] = data

    # ── Lead Management ───────────────────────────────────────────────────────

    def save_lead(self, lead_data: dict) -> str:
        lead_id = f"lead_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        if self.client:
            self.client.hset("ro_care:leads", lead_id, json.dumps(lead_data))
        else:
            if "leads" not in self._fallback:
                self._fallback["leads"] = {}
            self._fallback["leads"][lead_id] = lead_data
        return lead_id

    def get_all_leads(self) -> dict:
        if self.client:
            raw = self.client.hgetall("ro_care:leads")
            return {k: json.loads(v) for k, v in raw.items()}
        return self._fallback.get("leads", {})