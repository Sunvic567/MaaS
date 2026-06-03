#!/usr/bin/env python3
"""
MaaS — BYOD Database Setup
============================
Runs automatically when a BYOD tenant signs up via POST /setup.
Connects directly to their Postgres DB and creates everything needed.

Can also be run manually:
    python byod_setup.py \
        --url "postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres"
"""

import sys
import argparse
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


# ============================================================
#  SQL STEPS — only what BYOD clients need on their own DB
# ============================================================

STEPS = [
    (
        "Enable pgvector extension",
        """
        CREATE EXTENSION IF NOT EXISTS vector;
        """
    ),
    (
        "Enable uuid-ossp extension",
        """
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        """
    ),
    (
        "Create memories table",
        """
        CREATE TABLE IF NOT EXISTS memories (
          id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
          tenant_id     TEXT        NOT NULL,
          user_id       TEXT        NOT NULL,
          agent_id      TEXT        NOT NULL,
          content       TEXT        NOT NULL
                                    CHECK (char_length(content) BETWEEN 1 AND 10000),
          embedding     VECTOR(384),
          memory_type   TEXT        NOT NULL DEFAULT 'episodic'
                                    CHECK (memory_type IN ('episodic', 'semantic', 'summary')),
          metadata      JSONB       NOT NULL DEFAULT '{}',
          importance    FLOAT       NOT NULL DEFAULT 0.5
                                    CHECK (importance BETWEEN 0.0 AND 1.0),
          created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          last_accessed TIMESTAMPTZ,
          expires_at    TIMESTAMPTZ
        );
        """
    ),
    (
        "Create vector similarity index",
        """
        CREATE INDEX IF NOT EXISTS memories_vector_idx
          ON memories USING ivfflat (embedding vector_cosine_ops)
          WITH (lists = 100);
        """
    ),
    (
        "Create tenant + user + agent lookup index",
        """
        CREATE INDEX IF NOT EXISTS memories_lookup_idx
          ON memories (tenant_id, user_id, agent_id);
        """
    ),
    (
        "Create TTL expiry index",
        """
        CREATE INDEX IF NOT EXISTS memories_ttl_idx
          ON memories (expires_at)
          WHERE expires_at IS NOT NULL;
        """
    ),
    (
        "Create recency index",
        """
        CREATE INDEX IF NOT EXISTS memories_recency_idx
          ON memories (tenant_id, user_id, agent_id, created_at DESC);
        """
    ),
    (
        "Enable Row Level Security on memories",
        """
        ALTER TABLE memories ENABLE ROW LEVEL SECURITY;
        """
    ),
    (
        "Create tenant isolation RLS policy",
        """
        DROP POLICY IF EXISTS memories_isolation ON memories;

        CREATE POLICY memories_isolation ON memories
          FOR ALL
          USING (tenant_id = current_setting('app.tenant_id', TRUE));
        """
    ),
    (
        "Create match_memories search function",
        """
        CREATE OR REPLACE FUNCTION match_memories(
          query_embedding  VECTOR(384),
          match_count      INT,
          p_tenant_id      TEXT,
          p_user_id        TEXT,
          p_agent_id       TEXT,
          p_memory_type    TEXT DEFAULT NULL
        )
        RETURNS TABLE (
          id            UUID,
          content       TEXT,
          user_id       TEXT,
          agent_id      TEXT,
          memory_type   TEXT,
          metadata      JSONB,
          importance    FLOAT,
          created_at    TIMESTAMPTZ,
          last_accessed TIMESTAMPTZ,
          expires_at    TIMESTAMPTZ,
          similarity    FLOAT
        )
        LANGUAGE sql STABLE
        AS $$
          SELECT
            id,
            content,
            user_id,
            agent_id,
            memory_type,
            metadata,
            importance,
            created_at,
            last_accessed,
            expires_at,
            1 - (embedding <=> query_embedding) AS similarity
          FROM memories
          WHERE
            tenant_id  = p_tenant_id
            AND user_id  = p_user_id
            AND agent_id = p_agent_id
            AND (p_memory_type IS NULL OR memory_type = p_memory_type)
            AND (expires_at IS NULL OR expires_at > NOW())
          ORDER BY embedding <=> query_embedding
          LIMIT match_count;
        $$;
        """
    ),
    (
        "Verify setup — count tables created",
        """
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = 'memories';
        """
    ),
]


# ============================================================
#  CORE SETUP FUNCTION
#  Called by both the CLI and the FastAPI POST /setup endpoint
# ============================================================

def run_byod_setup(connection_string: str) -> dict:
    """
    Connect to a BYOD tenant's Postgres DB and run all setup steps.

    Args:
        connection_string: Full Postgres DSN.
                           e.g. postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres

    Returns:
        dict with keys: success (bool), steps_passed (list), steps_failed (list), error (str|None)
    """
    steps_passed = []
    steps_failed = []
    conn = None

    try:
        # Connect directly to their Postgres
        print(f"\n🔌  Connecting to database...")
        conn = psycopg2.connect(connection_string)

        # Extensions require AUTOCOMMIT — cannot run inside a transaction
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Run extensions first (need autocommit)
        for label, query in STEPS[:2]:
            try:
                cur.execute(query.strip())
                print(f"  ✅  {label}")
                steps_passed.append(label)
            except Exception as e:
                print(f"  ❌  {label}: {e}")
                steps_failed.append({"step": label, "error": str(e)})

        # Switch to transactional mode for the rest
        # If anything fails, roll back — no partial setup
        conn.set_isolation_level(0)  # back to default
        conn.autocommit = False

        try:
            for label, query in STEPS[2:]:
                cur.execute(query.strip())
                print(f"  ✅  {label}")
                steps_passed.append(label)

            conn.commit()
            print("\n✅  BYOD database setup complete.\n")

        except Exception as e:
            conn.rollback()
            print(f"\n❌  Setup failed at step — rolling back: {e}\n")
            steps_failed.append({"step": "transaction", "error": str(e)})
            return {
                "success": False,
                "steps_passed": steps_passed,
                "steps_failed": steps_failed,
                "error": str(e),
            }

    except psycopg2.OperationalError as e:
        print(f"\n❌  Could not connect to database: {e}\n")
        return {
            "success": False,
            "steps_passed": [],
            "steps_failed": [],
            "error": f"Connection failed: {str(e)}",
        }
    finally:
        if conn:
            conn.close()

    return {
        "success": len(steps_failed) == 0,
        "steps_passed": steps_passed,
        "steps_failed": steps_failed,
        "error": None,
    }


# ============================================================
#  VERIFY FUNCTION
#  Check if a DB has already been set up correctly
# ============================================================

def verify_byod_setup(connection_string: str) -> dict:
    """
    Check that the memories table, indexes, and function exist.
    Useful to call before routing requests to a BYOD DB.
    """
    checks = {
        "memories_table": """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'memories'
            );
        """,
        "vector_extension": """
            SELECT EXISTS (
                SELECT 1 FROM pg_extension WHERE extname = 'vector'
            );
        """,
        "match_memories_function": """
            SELECT EXISTS (
                SELECT 1 FROM pg_proc WHERE proname = 'match_memories'
            );
        """,
        "vector_index": """
            SELECT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE tablename = 'memories' AND indexname = 'memories_vector_idx'
            );
        """,
        "rls_enabled": """
            SELECT relrowsecurity FROM pg_class
            WHERE relname = 'memories' AND relnamespace = 'public'::regnamespace;
        """,
    }

    results = {}
    try:
        conn = psycopg2.connect(connection_string)
        cur = conn.cursor()
        for check_name, query in checks.items():
            cur.execute(query.strip())
            results[check_name] = cur.fetchone()[0]
        conn.close()
    except Exception as e:
        return {"verified": False, "error": str(e), "checks": {}}

    all_passed = all(results.values())
    return {
        "verified": all_passed,
        "checks": results,
        "error": None,
    }


# ============================================================
#  CLI ENTRYPOINT
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="MaaS BYOD Database Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup
  python byod_setup.py --url "postgresql://postgres:password@db.xyz.supabase.co:5432/postgres"

  # Verify only
  python byod_setup.py --url "postgresql://..." --verify-only

Find your connection string:
  Supabase Dashboard → Settings → Database → Connection string → URI
        """,
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Postgres connection string (URI format)",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify setup — do not run migrations",
    )

    args = parser.parse_args()

    print("\n🧠  MaaS — BYOD Database Setup")
    print("=" * 40)

    if args.verify_only:
        print("\n🔍  Verifying existing setup...\n")
        result = verify_byod_setup(args.url)
        if result["verified"]:
            print("✅  Database is correctly set up.\n")
        else:
            print("❌  Database is NOT fully set up.")
            for check, passed in result.get("checks", {}).items():
                status = "✅" if passed else "❌"
                print(f"   {status}  {check}")
            print()
        sys.exit(0 if result["verified"] else 1)

    result = run_byod_setup(args.url)

    print(f"Steps passed : {len(result['steps_passed'])}")
    print(f"Steps failed : {len(result['steps_failed'])}")

    if not result["success"]:
        print(f"\nError: {result['error']}")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()