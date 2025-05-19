from clickhouse_driver import Client
from dotenv import load_dotenv
import os
import json
from block_raw import BlockRaw

# Load environment variables
load_dotenv(override=True)

# Initialize ClickHouse client
client = Client(
    host=os.getenv("CLICKHOUSE_HOST"),
    port=int(os.getenv("CLICKHOUSE_PORT")),
    user=os.getenv("CLICKHOUSE_USER"),
    password=os.getenv("CLICKHOUSE_PASSWORD"),
)


def main():
    # Initialize BlockRaw with environment variables
    rpc_url = os.getenv("RPC_URL")
    start_block = int(os.getenv("START_BLOCK"))
    num_blocks = int(os.getenv("NUM_BLOCKS"))
    batch_size = int(os.getenv("BATCH_SIZE"))

    print("Using RPC:", os.getenv("RPC_URL"))
    print(
        f"Starting from block: {start_block}, for {num_blocks} blocks, with {batch_size} batch size"
    )
    block_fetcher = BlockRaw(
        rpc_url=rpc_url,
        start_block=start_block,
        num_blocks=num_blocks,
        batch_size=batch_size,
    )

    # Process blocks in batches
    while True:
        batch = block_fetcher.fetch_next_batch()
        if not batch:
            break

        # Insert all blocks in the batch
        insert_query = "INSERT INTO solana.raw (block_id, raw) VALUES"
        values = [
            (block_height, json.dumps(block_data)) for block_height, block_data in batch
        ]
        client.execute(insert_query, values)

        # Print the range of insert
        if batch:
            first_block = batch[0][0]
            last_block = batch[-1][0]
            print(f"Inserted blocks {first_block} to {last_block} into solana.raw.")


if __name__ == "__main__":
    main()
