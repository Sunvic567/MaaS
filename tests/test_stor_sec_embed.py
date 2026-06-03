from app.services.embeddings import embed_for_search, embed_for_storage
from app.db.client import get_master_client
from dotenv import load_dotenv
import asyncio
load_dotenv()

from app.schemas.memory import (
        GetContext, Is_Duplicate, MemoryCreate, MemoryDelete, MemorySearch, MemoryWipe, MemoryUpdate
)


from app.services.memory import get_context, is_duplicate, store_memory, search_memories, delete_memory, update_memory, wipe_memories, expire_memories

TENANT_ID = "cde6cfd6-4224-48da-8e5f-abcf25b9a01a"
USER_ID   = "user_001"
AGENT_ID  = "support_bot"
db = get_master_client()


load_1 =  MemoryCreate(
        user_id="user_001",
        agent_id="support_bot",
        content="User is based in Lagos, nigeria",
        memory_type="semantic",
        importance=0.8,
)

load_2 =  MemoryCreate(
        user_id="user_001",
        agent_id="support_bot",
        content="User prefers concise bullet points",
        memory_type="semantic",
        importance=0.7,
)

load_3 =  MemoryCreate(
        user_id="user_001",
        agent_id="support_bot",
        content="User is building a customer support agent",
        memory_type="semantic",
        importance=0.6,
)

load_4 =  MemoryCreate(
        user_id="user_001",
        agent_id="support_bot",
        content="Temporary note",
        memory_type="semantic",
        importance=0.5,
        ttl_days=1
)


print("=== 1. STORE ===")

mem_1 = asyncio.run(store_memory(
        payload=load_1,
        db= db,
        tenant_id=TENANT_ID
))
mem_2 = asyncio.run(store_memory(
        payload=load_2,
        db= db,
        tenant_id=TENANT_ID
))
mem_3 = asyncio.run(store_memory(
        payload=load_3,
        db= db,
        tenant_id=TENANT_ID
))
mem_4 = asyncio.run(store_memory(
        payload=load_4,
        db= db,
        tenant_id=TENANT_ID
))
assert mem_1 is not None, "store_memory failed for mem_1"
assert mem_2 is not None, "store_memory failed for mem_2"
assert mem_3 is not None, "store_memory failed for mem_3"
assert mem_4 is not None, "store_memory failed for mem_4"
 
print("\n=== 2. SEARCH ===")
search_load_1 = MemorySearch(
        query="Where does this user live?",
        user_id=USER_ID,  
        agent_id=AGENT_ID,
        top_k=3,
        min_score=0.0,
)
        
results = asyncio.run(search_memories(
        payload=search_load_1,
        db= db,
        tenant_id=TENANT_ID
))
for r in results.memories:
    print(f"  [{r.score:.3f}] {r.content}")

print("\n=== 3. TTL EXPIRY ===")
expired = asyncio.run(expire_memories(
        db= db
))
print(f"  Expired: {expired}")


print("\n=== 4. DELETE ONE ===")
assert mem_1 is not None and mem_1.id, "mem_1 must exist for deletion test"
del_load_1 = MemoryDelete(
        user_id=USER_ID,
        agent_id=AGENT_ID,
        memory_id=mem_1.id
)
del_mem =  asyncio.run(delete_memory(payload=del_load_1, db= db, tenant_id=TENANT_ID))
print(f"  Deleted: {del_mem.deleted}")   # should be True

print("\n=== 5. SEARCH AGAIN (Lagos should be gone) ===")

results = asyncio.run(search_memories(
        payload=search_load_1,
        db= db,
        tenant_id=TENANT_ID
))
for r in results.memories:
    print(f"  [{r.score:.3f}] {r.content}")

print("\n=== 6. WIPE ALL ===")
wipe_mem_1 = MemoryWipe(
        user_id=USER_ID,
        agent_id=AGENT_ID,
        confirm=True
)

wipe_mem = asyncio.run(wipe_memories(payload=wipe_mem_1, db= db, tenant_id=TENANT_ID))
print(f"  Wiped: {wipe_mem.deleted}")
assert wipe_mem.deleted > 0

print("\n=== 7. SEARCH AFTER WIPE (should return nothing) ===")
results = asyncio.run(search_memories(
             payload=MemorySearch(
            query="anything",
            user_id=USER_ID,
            agent_id=AGENT_ID,
            top_k=3,
            min_score=0.0
        ),
        db= db,
        tenant_id=TENANT_ID
))
for r in results.memories:
    print(f"  [{r.score:.3f}] {r.content}") # expect 0


# duplicate of load_1 — slightly different wording, same meaning
load_duplicate = MemoryCreate(
    user_id=USER_ID,
    agent_id=AGENT_ID,
    content="User lives in Lagos, Nigeria",
    memory_type="semantic",
    importance=0.9,
)
 
 
# ── STORE baseline memories ───────────────────────────────────────
 
print("=== SETUP: STORE BASE MEMORIES ===")
 
mem_1 = asyncio.run(store_memory(payload=load_1, db=db, tenant_id=TENANT_ID))
mem_2 = asyncio.run(store_memory(payload=load_2, db=db, tenant_id=TENANT_ID))
mem_3 = asyncio.run(store_memory(payload=load_3, db=db, tenant_id=TENANT_ID))
 
print(f"  Stored mem_1: {mem_1.id if mem_1 is not None else None}")
print(f"  Stored mem_2: {mem_2.id if mem_2 is not None else None}")
print(f"  Stored mem_3: {mem_3.id if mem_3 is not None else None}")
 
 
# ── 1. GET CONTEXT ────────────────────────────────────────────────
 
print("\n=== 1. GET CONTEXT ===")
 
context_1 = GetContext(
        user_id=USER_ID,
        agent_id=AGENT_ID,
)
context_2 = GetContext(
        user_id="goast_user",
        agent_id=AGENT_ID,
)
context = asyncio.run(get_context(
    payload=context_1,
    tenant_id=TENANT_ID,
    db=db,
    top_k=10,
))
 
print(f"  Total memories in context: {context.total}")
print("  Ranked by importance + recency:")
for m in context.memories:
    print(f"    [importance={m.importance}] {m.content}")
 
assert context.total >= 3, f"Expected at least 3, got {context.total}"
assert context.memories[0].importance >= context.memories[-1].importance, \
    "Memories should be sorted by importance descending"
 
 
# ── 2. IS DUPLICATE ───────────────────────────────────────────────
 
print("\n=== 2. IS DUPLICATE ===")
 
# Should be a duplicate — very similar to load_1
dub_load_1 = MemoryCreate(
        user_id=USER_ID,
        agent_id=AGENT_ID,
        content="User lives in Lagos, Nigeria",
)
dub_load_2 = MemoryCreate(
        user_id=USER_ID,
        agent_id=AGENT_ID,
        content="User has a dog named Max",
)

dub_data_check = Is_Duplicate(
        user_id=USER_ID,
        agent_id=AGENT_ID,
)
dup_check = asyncio.run(is_duplicate(
    content=dub_load_1.content,
    payload=dub_data_check,
    tenant_id=TENANT_ID,
    db=db,
    threshold=0.95,
))
print(f"  '{load_duplicate.content}' is duplicate: {dup_check}")
assert dup_check is True, "Expected duplicate to be detected"
 
# Should NOT be a duplicate — completely different content
unique_check = asyncio.run(is_duplicate(
    content=dub_load_2.content,
    payload=dub_data_check,
    tenant_id=TENANT_ID,
    db=db,
    threshold=0.95,
))
print(f"  'User has a dog named Max' is duplicate: {unique_check}")
assert unique_check is False, "Expected unique content to pass"
 
 
# ── 3. UPDATE MEMORY ──────────────────────────────────────────────
 
print("\n=== 3. UPDATE MEMORY ===")
 
# User moved cities — update mem_1 in place
assert mem_1 is not None and mem_1.id, "mem_1 must exist for update test"
mem_update_1 = MemoryUpdate(
        user_id=USER_ID,
        agent_id=AGENT_ID,
        memory_id=mem_1.id,
        new_content="User moved from Lagos to Abuja, Nigeria",
        importance=0.95,
)

mem_update_2 = MemoryUpdate(
        user_id=USER_ID,
        agent_id=AGENT_ID,
        memory_id="00000000-0000-0000-0000-000000000000",  # non-existent ID
        new_content="User moved from Lagos to Abuja, Nigeria",
        importance=0.95,
)

updated_mem_1 = asyncio.run(update_memory(
        payload=mem_update_1,
        tenant_id=TENANT_ID,
        db=db,
))
 
print(f"  Memory ID unchanged: {updated_mem_1.id == mem_1.id}")
print(f"  New content: {updated_mem_1.content}")
print(f"  New importance: {updated_mem_1.importance}")
 
assert updated_mem_1.id == mem_1.id, "Memory ID should not change on update"
assert updated_mem_1.content == "User moved from Lagos to Abuja, Nigeria"
assert updated_mem_1.importance == 0.95
 
# Verify update is reflected in context
print("\n  Verifying update in get_context()...")
context_after = asyncio.run(get_context(
    payload=context_2,
    tenant_id=TENANT_ID,
    db=db,
    top_k=10,
))
 
contents = [m.content for m in context_after.memories]
assert "User moved from Lagos to Abuja, Nigeria" in contents, \
    "Updated content should appear in context"
assert "User is based in Lagos, Nigeria" not in contents, \
    "Old content should be gone"
print("  ✅ Context reflects updated memory correctly")
 
 
# ── 4. UPDATE: invalid memory_id ─────────────────────────────────
 
print("\n=== 4. UPDATE WITH INVALID ID (should raise) ===")
 
try:
    updated_mem_2 = asyncio.run(update_memory(
        payload=mem_update_2,
        tenant_id=TENANT_ID,
        db=db,
    ))
    print("❌ Should have raised ValueError")
except ValueError as e:
    
    print(f"✅ Caught expected error: {e}")

 
# ── 5. GET CONTEXT: empty user ────────────────────────────────────
 
print("\n=== 5. GET CONTEXT FOR UNKNOWN USER (should return empty) ===")
 
empty_context = asyncio.run(get_context(
        payload=context_2,
    tenant_id=TENANT_ID,
    db=db,
    top_k=10,
))
 
print(f"  Memories returned: {empty_context.total}")
assert empty_context.total == 0, "Unknown user should have no memories"
print("  ✅ Correctly returned empty context")
 
print("\n✅ All tests passed.")
 
 