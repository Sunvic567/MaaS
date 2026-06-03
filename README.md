# maas-py

Persistent memory for AI agents. One API key. Five endpoints.

## Install

```bash
pip install maas-py
```

## Quick Start

```python
from maas import MaaSClient

client = MaaSClient(
    api_key="maas_live_xxx",
    base_url="https://your-app.onrender.com",
)

# Store a memory
mem_id = client.remember(
    "User prefers dark mode",
    user_id="user_001",
    agent_id="support_bot",
)

# Recall relevant memories
memories = client.recall(
    "What UI preferences does this user have?",
    user_id="user_001",
    agent_id="support_bot",
)

for m in memories:
    print(m.content, m.score)

# Load context at session start
context = client.context(user_id="user_001", agent_id="support_bot")

# Forget everything
client.forget_all(user_id="user_001", agent_id="support_bot")
```

## LangGraph Integration

```python
from maas import AsyncMaaSClient
from langgraph.graph import StateGraph

client = AsyncMaaSClient(api_key="maas_live_xxx")

async def load_memory(state):
    memories = await client.recall(
        query=state["user_message"],
        user_id=state["user_id"],
        agent_id="my_agent",
    )
    state["context"] = [m.content for m in memories]
    return state

async def save_memory(state):
    await client.remember(
        content=state["user_message"],
        user_id=state["user_id"],
        agent_id="my_agent",
        memory_type="episodic",
    )
    return state
```