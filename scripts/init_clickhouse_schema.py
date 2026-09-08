#!/usr/bin/env python3
"""
ClickHouse Schema Initializer for StudioSonar.
Executes infra/clickhouse_schema.sql against the configured ClickHouse cluster.
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("init_clickhouse_schema")

def main():
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "infra", "clickhouse_schema.sql")
    if not os.path.exists(schema_path):
        logger.error(f"Schema file not found at {schema_path}")
        sys.exit(1)

    with open(schema_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    from dotenv import load_dotenv
    load_dotenv()

    host = os.getenv("CLICKHOUSE_HOST", "localhost")
    port = int(os.getenv("CLICKHOUSE_PORT", "8443" if "clickhouse.cloud" in host else "8123"))
    user = os.getenv("CLICKHOUSE_USER", "default")
    password = os.getenv("CLICKHOUSE_PASSWORD", "")
    database = os.getenv("CLICKHOUSE_DATABASE", "default")
    secure = (port == 8443) or ("clickhouse.cloud" in host)

    logger.info(f"Connecting to ClickHouse at {host}:{port} (secure={secure}, db={database})...")

    try:
        import clickhouse_connect
        client = clickhouse_connect.get_client(
            host=host,
            port=port,
            username=user,
            password=password,
            database=database,
            secure=secure,
            connect_timeout=30,
            send_receive_timeout=30
        )
        
        # Split statements by semicolon
        statements = [s.strip() for s in sql_content.split(";") if s.strip() and not s.strip().startswith("--")]
        logger.info(f"Executing {len(statements)} DDL statements from infra/clickhouse_schema.sql...")
        
        for i, stmt in enumerate(statements, 1):
            # Skip pure comments
            lines = [l for l in stmt.splitlines() if not l.strip().startswith("--")]
            clean_stmt = "\n".join(lines).strip()
            if not clean_stmt:
                continue
            logger.info(f"[{i}/{len(statements)}] Executing DDL block...")
            client.command(clean_stmt)

        logger.info("✅ All ClickHouse schemas, tables, and materialized views initialized successfully!")
    except ImportError:
        logger.warning("clickhouse-connect package not installed. Install with: pip install clickhouse-connect")
        logger.info(f"You can also run infra/clickhouse_schema.sql directly using clickhouse-client or ClickHouse Cloud SQL Console.")
    except Exception as e:
        logger.error(f"Failed to execute ClickHouse schema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
