import sys
import os

# ── Yeh line zaroori hai — project root path set karta hai ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

import uuid
from chatbot import RiyaChatbot

def main():
    print("=" * 50)
    print("  RO Care India — Riya Chatbot (Test Mode)  ")
    print("=" * 50)
    print("Commands: 'quit' = exit | 'leads' = all leads | 'new' = new session\n")

    bot        = RiyaChatbot()
    session_id = input("Session ID (Enter for new): ").strip() or f"session_{uuid.uuid4().hex[:8]}"
    print(f"📍 Session: {session_id}\n")

    # Opening message
    opening = bot.chat(session_id, "  ")
    print(f"Riya: {opening}\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        if user_input.lower() == "new":
            session_id = f"session_{uuid.uuid4().hex[:8]}"
            print(f"📍 New session: {session_id}\n")
            opening = bot.chat(session_id, "Hello")
            print(f"Riya: {opening}\n")
            continue

        if user_input.lower() == "leads":
            leads = bot.memory.get_all_leads()
            print(f"\n📋 Total Leads: {len(leads)}")
            for lid, ldata in leads.items():
                print(f"  {lid}: {ldata}")
            print()
            continue

        response = bot.chat(session_id, user_input)
        print(f"\nRiya: {response}\n")

if __name__ == "__main__":
    main()