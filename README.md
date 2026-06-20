# MemLayer

**MemLayer** is a FastAPI backend plus Python SDK for persistent memory in AI agents.

- `app/` contains the backend API and webhook handlers.
- `sdk/` contains the `memlayer-py` Python SDK for storing, recalling, and managing memories.

## Project overview

MemLayer stores user-specific memories for agents so they can recall preferences, context, and facts across conversations.

Key capabilities:
- Store memories with `user_id` + `agent_id`
- Search memories by semantic similarity + recency + importance
- Keep session context consistent across requests
- Wipe, update, and deduplicate memories
- Support free signups and payment webhooks via Flutterwave
- Send API keys by email using Resend

## Repository structure

- `app/` — FastAPI application
  - `api/` — route modules
  - `core/` — config, auth, and error handling
  - `db/` — Supabase client and migration SQL
  - `services/` — memory, email, embeddings business logic
- `sdk/` — Python SDK package for consuming MemLayer
- `tests/` — backend tests
- `.env` — local environment variables
- `pyproject.toml` — backend dependencies and metadata

## Running the backend locally

1. Copy `.env` and fill in your keys:

```env
SUPABASE_URL=<your-supabase-url>
SUPABASE_SERVICE_KEY=<your-service-role-key>
OPENAI_API_KEY=<your-openai-key>
MAAS_MASTER_KEY=<master-key>
FLUTTERWAVE_SECRET_HASH=<flutterwave-secret-hash>
RESEND_API_KEY=<your-resend-key>
RESEND_FROM_EMAIL=support@memlayer.online
ENVIRONMENT=development
```

2. Install dependencies:

```bash
py -3 -m pip install -r requirements.txt
```

3. Start the app:

```bash
py -3 -m uvicorn app.main:app --reload
```

4. Open the API docs:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## API endpoints

- `POST /memories` — Store a memory
- `GET /memories/search` — Search memories
- `GET /memories/context` — Load session context
- `GET /memories` — List memories
- `PATCH /memories/{memory_id}` — Update a memory
- `DELETE /memories/{memory_id}` — Delete a memory
- `DELETE /memories` — Wipe memories
- `POST /webhooks/signup/free` — Free signup webhook
- `POST /webhooks/flutterwave` — Payment webhook
- `POST /admin/tenants` — Create a tenant via master key

## SDK package

The SDK is packaged in `sdk/` as `memlayer-py`. Use it for client-side storage and retrieval.

For SDK usage, see `sdk/README.md`.

## Notes

- The webhook route `POST /webhooks/flutterwave` is a notification endpoint, not a checkout redirect.
- Resend requires the sending domain to be verified. Set `RESEND_FROM_EMAIL` to a verified address in `.env`.
- The backend uses Supabase for tenancy, storage, and vector search.

## Contributing

1. Fork the repo
2. Create a branch
3. Make your changes
4. Submit a pull request

---

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
- [GitHub](https://github.com/sunvic67/memlayer)
- [Report a Bug](https://github.com/sunvic67/memlayer/issues)
- [Email](mailto:support@memlayer.online)

---

## License

MIT — see [LICENSE](LICENSE) for details.