# memlayer-py

A lightweight Python SDK for MemLayer: persistent memory storage and retrieval for AI agents.

## Install

```bash
pip install memlayer-py
```

## Quick Start

```python
from memlayer import MemLayerClient

client = MemLayerClient(
    api_key="ml_live_xxx",
    base_url="https://memlayer.online",
)

result = client.remember(
    "User prefers dark mode",
    user_id="user_123",
    agent_id="support_bot",
)

memories = client.recall(
    "What does this user prefer?",
    user_id="user_123",
    agent_id="support_bot",
)

for memory in memories:
    print(memory.content, memory.score)
```

## How it works

The SDK wraps MemLayer REST endpoints with a simple client interface.

### Sync client

Use `MemLayerClient` for synchronous applications:

```python
from memlayer import MemLayerClient

client = MemLayerClient(api_key="ml_live_xxx")
```

### Async client

Use `AsyncMemLayerClient` for async apps and frameworks like FastAPI:

```python
from memlayer import AsyncMemLayerClient

async with AsyncMemLayerClient(api_key="ml_live_xxx") as client:
    await client.remember(
        "User prefers concise responses",
        user_id="user_123",
        agent_id="support_bot",
    )
```

## Client methods

### `remember(...)`
Store a memory for a user+agent pair.

### `recall(...)`
Search memories using semantic similarity plus recency and importance.

### `context(...)`
Load contextual memories for the start of a session.

### `list(...)`
List stored memories with pagination.

### `update(...)`
Update an existing memory with new content.

### `forget(...)`
Delete a single memory by ID.

### `forget_all(...)`
Wipe all memories for a user+agent pair.

### `is_duplicate(...)`
Check whether a memory already exists before storing.

## Configuration

- `api_key`: required
- `base_url`: defaults to `https://memlayer.online`
- `timeout`: request timeout in seconds

## Error handling

The SDK raises custom exceptions for common API failures:

- `AuthenticationError`
- `PlanLimitError`
- `MemoryNotFoundError`
- `DuplicateMemoryError`
- `MemLayerError`

## Package info

Package name: `memlayer-py`
Version: `0.1.3`

## Contributing

If you want to improve the SDK:

1. Fork the repo
2. Update `sdk/README.md`
3. Submit a PR

## License

MIT License
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
- [API Docs](https://doc.memlayer.online)
- [GitHub](https://github.com/sunvic567/memlayer)
- [Report a Bug](https://github.com/sunvic567/memlayer/issues)
- [Email](mailto:support@memlayer.online)

---

## License

MIT — see [LICENSE](LICENSE) for details.