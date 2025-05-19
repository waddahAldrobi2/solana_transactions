import requests
import json
from typing import Dict, Any, Tuple, List
from dataclasses import dataclass


@dataclass
class BlockRaw:
    """Class for fetching and storing raw block data from Solana RPC."""

    rpc_url: str
    start_block: int
    num_blocks: int
    batch_size: int = 10

    def __init__(
        self, rpc_url: str, start_block: int, num_blocks: int, batch_size: int
    ):
        """
        Initialize BlockRaw with required parameters.

        Args:
            rpc_url: The Solana RPC endpoint URL
            start_block: The starting block height to fetch from
            num_blocks: The number of blocks to fetch
            batch_size: Number of blocks to fetch in each batch (default: 10)
        """
        self.rpc_url = rpc_url
        self.start_block = start_block
        self.num_blocks = num_blocks
        self.batch_size = batch_size
        self.current_index = 0

    def get_block(self, block_slot: int) -> Dict[str, Any]:
        """Fetch block details from Solana RPC for a given block slot."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBlock",
            "params": [
                block_slot,
                {
                    "encoding": "json",
                    "transactionDetails": "full",
                    "maxSupportedTransactionVersion": 0,
                    "rewards": False,
                },
            ],
        }
        response = requests.post(self.rpc_url, json=payload)
        return response.json()

    def fetch_next_batch(self) -> List[Tuple[int, Dict[str, Any]]]:
        """
        Fetch the next batch of blocks.

        Returns:
            List[Tuple[int, Dict[str, Any]]]: List of (block_height, block_data) tuples for the batch.
            Empty list if no more blocks to fetch.
        """
        if self.current_index >= self.num_blocks:
            return []

        batch = []
        end_index = min(self.current_index + self.batch_size, self.num_blocks)

        for i in range(self.current_index, end_index):
            block_slot = self.start_block + i
            print(f"\nFetching details for block {block_slot}...")

            try:
                block_data = self.get_block(block_slot)
                if not block_data.get("result", None):
                    print(f"Block {block_slot} is skipped")
                else:
                    batch.append((block_slot, block_data))
            except Exception as e:
                print(f"Error processing block {block_slot}: {str(e)}")
                continue

        self.current_index = end_index
        return batch
