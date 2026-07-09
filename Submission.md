# Remem — Memory-as-a-Service for AI Agents
### AMD Developer Hackathon: ACT II — Unicorn Track

---

## What is Remem?

Remem is memory infrastructure for AI agents. A dead-simple API that gives any agent
persistent, semantically-ranked memory — across sessions, users, and agent frameworks.

Every AI agent built today has the same silent flaw: it forgets. Not because developers
want it to — but because there is no standard, lightweight way to give agents persistent
memory. Developers are left dumping full conversation history into every prompt, building
custom vector logic from scratch, or accepting stateless agents that frustrate users.

Remem fixes this with two API calls.

```python
# Store a memory
client.store("User is on the Pro plan and prefers email contact")

# Retrieve relevant context before responding
context = client.get_context("What do I know about this user?")
```

That is the entire integration. No vector database to configure. No embedding pipeline
to maintain. No scoring logic to write.

---

## What Makes Remem Different

**Other solutions do cosine similarity and call it memory. Remem does not.**

### 1. Hybrid Scoring — Not Dumb Retrieval

Remem scores every memory on three axes simultaneously:

- 70% semantic relevance (cosine similarity)
- 20% recency decay (recent memories rank higher)
- 10% importance weighting (developer-assigned priority)

The agent gets the *right* memories ranked by what matters right now — not just
the most semantically similar ones. That is the difference between retrieval and judgment.

### 2. Memory That Manages Itself

Remem has TTL-based expiry via pg_cron — memories age out automatically based on
rules you define. Duplicate detection at 0.95 cosine similarity prevents the same
fact being stored dozens of times. The memory layer runs itself. You do not babysit it.

### 3. BYOD — Your Data Never Leaves Your Infrastructure

Every other memory API stores your users' data on their servers.
Remem's Bring Your Own Database (BYOD) Supabase option means enterprise customers
connect their own database. Remem runs the logic. The data never touches Remem's
infrastructure. That answers every enterprise compliance question before it gets asked.

---

## AMD Integration

Remem's embedding generation runs through Fireworks AI, which operates on
AMD Instinct MI300X GPUs via ROCm.

**Model:** `nomic-ai/nomic-embed-text-v1.5` (768 dimensions)
**Hardware:** AMD Instinct MI300X via Fireworks AI
**Benchmark endpoint:** `https://api.remem.online/benchmark`

Every memory stored and every retrieval query generates embeddings on AMD hardware.
At scale, embedding throughput directly determines API latency —
AMD MI300X is what makes Remem fast enough for real-time agent loops.

---

## Live Benchmarks

Hit the live endpoint: `https://api.remem.online/benchmark`

| Metric | Result |
|--------|--------|
| Embedding avg latency | 418.73ms |
| Embedding min latency | 312.89ms |
| Embedding max latency | 507.28ms |
| Samples | 5 |
| Errors | 0 |
| Embedding model | nomic-embed-text-v1.5 |
| Vector dimensions | 768 |
| Hardware | AMD Instinct MI300X via Fireworks AI |

> Latency measured end-to-end including network round-trip 
> from West Africa to Fireworks AI inference servers. 
> Raw AMD MI300X GPU inference time is estimated at 20-50ms. 
> Developers closer to Fireworks AI server regions 
> (US/EU) will see significantly lower end-to-end latency.
---

## The Product is Real

This is not a hackathon prototype.

- ✅ FastAPI backend — deployed and live on Render
- ✅ Supabase pgvector — multi-tenant memory storage
- ✅ Python SDK — `pip install remem-py` (published on PyPI)
- ✅ API documentation — Mintlify docs at remem.online/docs
- ✅ Landing page — remem.online
- ✅ BYOD Supabase — enterprise data sovereignty option
- ✅ Flutterwave payment integration — tenant provisioning on payment

---

## Quick Start

```bash
git clone https://github.com/sunvic567/remem
cd remem
git checkout amd-hackathon
cp .env.example .env
# Fill in your credentials in .env
docker compose up
```

API will be available at `http://localhost:8000`
Benchmark endpoint: `http://localhost:8000/benchmark`

---

## Demo Agent

See `demo/support_agent.py` — a customer support agent showing the before/after
contrast of an agent without Remem versus an agent with Remem across three sessions.

Run the demo:

```bash
cd demo
pip install -r requirements.txt
cp .env.example .env
python support_agent.py
```

---

## Roadmap

- Multi-modal memory (images, audio, documents)
- Memory analytics dashboard — tenant-level insights
- MCP integration — Remem as a native memory server for MCP-compatible agents
- Memory compression — intelligent summarization of aging memories

---

## Links

- Product: https://dev.remem.online
- Docs: https://docs.remem.online
- PyPI: https://pypi.org/project/remem-py
- GitHub: https://github.com/yourusername/remem/tree/amd-hackathon
- Benchmark: https://api.remem.online/benchmark