"""
Remem Demo — Persistent Memory for AI Agents
Shows the same customer support agent with and without Remem.
Uses: remem-py SDK + LangChain Google Gemini
"""

import os
import random
import time
from typing import Any, Callable

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from remem import RememClient

load_dotenv()

# ── Clients ──────────────────────────────────────────────────
remem = RememClient(
    api_key  = os.getenv("REMEM_API_KEY") or "",
    base_url = "https://api.remem.online"
)

llm = ChatGoogleGenerativeAI(
    model      = "gemini-2.5-flash",
    google_api_key = os.getenv("GEMINI_API_KEY"),
    temperature    = 0.7
)

DIVIDER = "\n" + "─" * 60 + "\n"
MAX_RETRIES = 3
BASE_DELAY_SECONDS = 1.0
MAX_DELAY_SECONDS = 10.0
AGENT_ID = "support_bot"


def _call_with_rate_limit(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Retry transient rate-limit and timeout failures with exponential backoff."""
    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # pragma: no cover - defensive wrapper
            last_error = exc
            message = str(exc).lower()
            is_rate_limit = any(
                token in message
                for token in (
                    "rate limit",
                    "429",
                    "too many requests",
                    "temporarily unavailable",
                    "quota exceeded",
                    "resource exhausted",
                    "timeout",
                )
            )

            if not is_rate_limit or attempt == MAX_RETRIES - 1:
                raise

            delay = min(BASE_DELAY_SECONDS * (2**attempt) + random.uniform(0, 0.5), MAX_DELAY_SECONDS)
            time.sleep(delay)

    if last_error is not None:
        raise last_error

    raise RuntimeError("Rate-limit protection failed unexpectedly")


# ── Agent WITHOUT memory ──────────────────────────────────────
def agent_without_memory(user_message: str) -> str:
    """Stateless agent — no memory, starts fresh every session."""
    messages = [
        SystemMessage(content=(
            "You are a helpful customer support agent. "
            "You have no history with this user. "
            "Ask for any information you need."
        )),
        HumanMessage(content=user_message)
    ]
    response = _call_with_rate_limit(llm.invoke, messages)
    return str(response.content)


# ── Agent WITH memory ─────────────────────────────────────────
def agent_with_memory(user_id: str, user_message: str) -> str:
    """Memory-powered agent — recalls everything via Remem."""

    # Pull relevant context from Remem before responding
    memories = _call_with_rate_limit(
        remem.recall,
        query=user_message,
        user_id=user_id,
        agent_id=AGENT_ID,
        top_k=5,
    )
    context = "\n".join([m.content for m in memories]) if memories else ""

    messages = [
        SystemMessage(content=(
            "You are a helpful customer support agent.\n\n"
            "Here is what you remember about this user:\n"
            f"{context if context else 'No prior history with this user.'}\n\n"
            "Use this context to give a warm, informed response. "
            "Never ask for information you already know."
        )),
        HumanMessage(content=user_message)
    ]

    response = _call_with_rate_limit(llm.invoke, messages)
    reply    = str(response.content)

    # Store this interaction in Remem for future sessions
    _call_with_rate_limit(
        remem.remember,
        content=f"User: {user_message} | Agent: {reply[:300]}",
        user_id=user_id,
        agent_id=AGENT_ID,
    )

    return reply


# ── Demo runner ───────────────────────────────────────────────
def run_demo():
    user_id = "demo_user_001"

    conversations = [
        "Hi, I'm Alex. I'm on the Pro plan and I'm having trouble with my API key — it keeps returning 401.",
        "I'm still having issues. Can you help?",
        "Same problem again. This is really frustrating.",
    ]

    print(DIVIDER)
    print("🔴  AGENT WITHOUT REMEM")
    print("    Every session starts from scratch.")
    print(DIVIDER)

    for i, message in enumerate(conversations, 1):
        print(f"Session {i}")
        print(f"User : {message}")
        print(f"Agent: {agent_without_memory(message)}")
        print(DIVIDER)

    print(DIVIDER)
    print("🟢  AGENT WITH REMEM")
    print("    Memory persists across every session.")
    print(DIVIDER)

    for i, message in enumerate(conversations, 1):
        print(f"Session {i}")
        print(f"User : {message}")
        print(f"Agent: {agent_with_memory(user_id, message)}")
        print(DIVIDER)

    print("✅  Demo complete.")
    print("    Notice how the Remem-powered agent remembers Alex's")
    print("    name, plan, and issue — without being told again.")
    print(DIVIDER)


if __name__ == "__main__":
    run_demo()