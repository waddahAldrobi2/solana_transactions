CREATE TABLE IF NOT EXISTS solana.raw (
    block_id UInt64,
    raw String,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (block_id); 