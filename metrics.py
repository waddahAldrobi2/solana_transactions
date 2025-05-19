from clickhouse_driver import Client
from block_metrics_processor import BlockMetricsProcessor


def main():
    try:
        # Connect to ClickHouse
        client = Client(host="localhost", port=8002, user="default", password="")

        # Query to get all blocks from raw table
        select_query = "SELECT block_id, raw FROM solana.raw"
        raw_blocks = client.execute(select_query)

        # Create processor instance and process metrics
        processor = BlockMetricsProcessor()
        block_metrics_data = processor.prepare_metrics_data(raw_blocks)

        print("Computing metrics for blocks...")

        # Insert metrics into ClickHouse
        if block_metrics_data:
            insert_query = """
            INSERT INTO solana.block_metrics 
            (block_id, 
            block_timestamp, 
            block_hash, 
            total_txns, 
            total_non_vote_txns, 
            total_vote_txns, 
            total_fees, 
            total_compute)
            
            VALUES
            """
            client.execute(insert_query, block_metrics_data)
            print(
                f"Successfully inserted metrics for {len(block_metrics_data)} blocks into ClickHouse"
            )

    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
