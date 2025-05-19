CREATE TABLE IF NOT EXISTS solana.block_metrics (
    block_id UInt64,
    block_timestamp DateTime,
    block_hash String,
    total_txns UInt64,
    total_fees UInt64,
    total_non_vote_txns UInt64,
    total_vote_txns UInt64,
    total_compute UInt64,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (block_id); 