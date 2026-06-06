# memlayer-py

> Persistent memory for AI agents. One API key. Your agent remembers everything.

[![PyPI version](https://badge.fury.io/py/memlayer-py.svg)](https://badge.fury.io/py/memlayer-py)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## The Problem

Every time a user starts a new conversation with your AI agent, it starts from zero. It doesn't remember their name, their preferences, what they complained about last week, or anything they've ever told it. You're either stuffing conversation history into the system prompt and hitting token limits, or your agent is asking the same questions over and over.

**MemLayer fixes that.**

---

## Install

```bash
pip install memlayer-py
```

---

## Quick Start

```python
from memlayer import MemLayerClient

client = MemLayerClient(
    api_key="ml_live_xxx",
    base_url="https://memlayer.online",
)

# Store what your agent learns
client.remember(
    "User prefers concise bullet points over long paragraphs",
    user_id="user_123",
    agent_id="support_bot",
    memory_type="semantic",
    importance=0.8,
)

# Load context at the start of every session
context = client.context(user_id="user_123", agent_id="support_bot")
for m in context.memories:
    print(m.content)

# Search when the user asks something
memories = client.recall(
    "what are this user's communication preferences?",
    user_id="user_123",
    agent_id="support_bot",
)
for m in memories:
    print(f"[{m.score:.3f}] {m.content}")
```

---

## Get an API Key

1. Visit [memlayer.online](https://memlayer.online)
2. Sign up for a free account
3. Copy your API key (`ml_live_xxx`)

Free plan includes 500 memories and 100 requests per day — enough to build and test your agent fully.

---

## Core Methods

### `remember()` — Store a memory

```python
result = client.remember(
    content="User is based in Lagos, Nigeria",
    user_id="user_123",
    agent_id="support_bot",
    memory_type="semantic",   # episodic | semantic | summary
    importance=0.8,           # 0.0 (low) to 1.0 (high)
    ttl_days=30,              # auto-expire after 30 days. None = permanent
)

print(result.id)             # memory UUID
print(result.is_duplicate)   # True if already stored
```

### `recall()` — Semantic search

```python
memories = client.recall(
    query="what does this user prefer?",
    user_id="user_123",
    agent_id="support_bot",
    top_k=5,        # return top 5 results
    min_score=0.70, # minimum relevance threshold
)

for m in memories:
    print(m.content)      # memory text
    print(m.score)        # hybrid relevance score
    print(m.importance)   # importance weight
    print(m.memory_type)  # episodic | semantic | summary
```

Retrieval uses hybrid scoring — **70% semantic similarity + 20% recency + 10% importance** — so the most relevant and recent memories always rank first.

### `context()` — Load session context

```python
# Call this at the start of every conversation
context = client.context(
    user_id="user_123",
    agent_id="support_bot",
    top_k=10,

    # Optional: pass the user's first message for smarter retrieval
    current_message="I need help with my order",
)

# Inject into your system prompt
system_prompt = "You are a helpful assistant.\n\nWhat you know about this user:\n"
for m in context.memories:
    system_prompt += f"- {m.content}\n"
```

### `update()` — Update a memory

```python
# User moved cities — update the old memory in place
updated = client.update(
    memory_id="775263ee-73af-4416-9804-1f274048ae08",
    user_id="user_123",
    agent_id="support_bot",
    new_content="User moved from Lagos to Abuja, Nigeria",
    importance=0.95,
)

print(updated.content)  # "User moved from Lagos to Abuja, Nigeria"
```

Same memory ID — just new content and a fresh embedding. No duplicate memories.

### `forget()` — Delete one memory

```python
result = client.forget(
    memory_id="775263ee-73af-4416-9804-1f274048ae08",
    user_id="user_123",
    agent_id="support_bot",
)
print(result.deleted)  # 1
```

### `forget_all()` — Wipe all memories

```python
# Use for GDPR requests or account resets
result = client.forget_all(user_id="user_123", agent_id="support_bot")
print(result.deleted)  # number of memories deleted
```

### `is_duplicate()` — Check before storing

```python
# Optional — remember() already checks internally
# Use this when you want to check without committing to store
already_known = client.is_duplicate(
    content="User is based in Lagos",
    user_id="user_123",
    agent_id="support_bot",
    threshold=0.95,
)

if not already_known:
    client.remember("User is based in Lagos", user_id="user_123", agent_id="support_bot")
```

### `list()` — Browse all memories

```python
# Paginate through all stored memories
page = client.list(
    user_id="user_123",
    agent_id="support_bot",
    limit=20,
    offset=0,
)

print(f"Total: {page.total}")
for m in page.memories:
    print(m.content, m.created_at)
```

---

## Memory Types

| Type | Use For | Example |
|---|---|---|
| `episodic` | Things that happened | "User complained about slow delivery" |
| `semantic` | Facts about the user | "User is based in Lagos, Nigeria" |
| `summary` | Compressed older memories | Auto-generated by MemLayer |

---

## Async Support

For LangGraph, FastAPI, and any async application:

```python
from memlayer import AsyncMemLayerClient

async def main():
    async with AsyncMemLayerClient(api_key="ml_live_xxx") as client:

        # Store
        result = await client.remember(
            "User prefers dark mode",
            user_id="user_123",
            agent_id="support_bot",
        )

        # Search
        memories = await client.recall(
            "UI preferences",
            user_id="user_123",
            agent_id="support_bot",
        )
```

---

## LangGraph Integration

Drop MemLayer into any LangGraph graph as store and retrieve nodes:

```python
from memlayer import AsyncMemLayerClient
from langgraph.graph import StateGraph, MessagesState

maas = AsyncMemLayerClient(api_key="ml_live_xxx")


async def load_memory(state: MessagesState):
    """Load relevant memories before the agent responds."""
    last_message = state["messages"][-1].content

    memories = await maas.recall(
        query=last_message,
        user_id=state["user_id"],
        agent_id="my_agent",
        top_k=5,
    )

    memory_context = "\n".join(f"- {m.content}" for m in memories)
    state["memory_context"] = memory_context
    return state


async def save_memory(state: MessagesState):
    """Save what the agent learned after responding."""
    last_message = state["messages"][-1].content

    await maas.remember(
        content=last_message,
        user_id=state["user_id"],
        agent_id="my_agent",
        memory_type="episodic",
    )
    return state


# Wire into your graph
builder = StateGraph(MessagesState)
builder.add_node("load_memory", load_memory)
builder.add_node("agent", your_agent_node)
builder.add_node("save_memory", save_memory)

builder.add_edge("load_memory", "agent")
builder.add_edge("agent", "save_memory")
```

---

## Error Handling

```python
from memlayer import (
    MemLayerClient,
    AuthenticationError,
    PlanLimitError,
    MemoryNotFoundError,
    DuplicateMemoryError,
    MemLayerError,
)

client = MemLayerClient(api_key="ml_live_xxx")

try:
    result = client.remember(
        "User prefers dark mode",
        user_id="user_123",
        agent_id="support_bot",
    )

except AuthenticationError:
    print("Invalid API key — check your ml_live_xxx key")

except PlanLimitError:
    print("Memory limit reached — upgrade your plan at memlayer.online")

except DuplicateMemoryError:
    print("This memory already exists — skipped")

except MemoryNotFoundError:
    print("Memory ID not found")

except MemLayerError as e:
    print(f"API error {e.status_code}: {e.detail}")
```

---

## Context Manager

```python
# Sync
with MemLayerClient(api_key="ml_live_xxx") as client:
    client.remember("something", user_id="u1", agent_id="bot")

# Async
async with AsyncMemLayerClient(api_key="ml_live_xxx") as client:
    await client.remember("something", user_id="u1", agent_id="bot")
```

---

## Pricing

| Plan | Memories | Requests/day | Price |
|---|---|---|---|
| Free | 500 | 100 | $0/mo |
| Pro | 50,000 | 10,000 | $19/mo |
| Enterprise | Unlimited | Unlimited | $99+/mo |

Enterprise includes BYOD (Bring Your Own Database) — your data never leaves your Supabase instance.

---

## REST API

You don't need the SDK — every method maps to a REST endpoint:

```bash
# Store
curl -X POST https://memlayer.online/memories \
  -H "X-API-Key: ml_live_xxx" \
  -H "Content-Type: application/json" \
  -d '{"content": "User prefers dark mode", "user_id": "u1", "agent_id": "bot"}'

# Search
curl "https://memlayer.online/memories/search?query=preferences&user_id=u1&agent_id=bot" \
  -H "X-API-Key: ml_live_xxx"

# Context
curl "https://memlayer.online/memories/context?user_id=u1&agent_id=bot" \
  -H "X-API-Key: ml_live_xxx"
```

Full API reference at [memlayer.online/docs](https://memlayer.online/docs).

---

## Links

- [Website](https://memlayer.online)
- [API Docs](https://memlayer.online/docs)
- [GitHub](https://github.com/yourusername/memlayer)
- [Report a Bug](https://github.com/yourusername/memlayer/issues)
- [Email](mailto:support@memlayer.online)

---

## License

MIT — see [LICENSE](LICENSE) for details.