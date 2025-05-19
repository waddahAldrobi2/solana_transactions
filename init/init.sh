#!/bin/bash
set -e

# Wait for ClickHouse to be ready
until clickhouse-client --query "SELECT 1" >/dev/null 2>&1; do
    echo "Waiting for ClickHouse to be ready..."
    sleep 1
done

# Execute the SQL files one at a time
clickhouse-client < /docker-entrypoint-initdb.d/01_create_db.sql
clickhouse-client < /docker-entrypoint-initdb.d/02_create_raw_table.sql
clickhouse-client < /docker-entrypoint-initdb.d/03_create_metrics_table.sql 