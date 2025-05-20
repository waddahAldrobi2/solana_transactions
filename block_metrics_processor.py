from datetime import datetime
import json
import base58
from constants import VOTE_INSTRUCTION_DISCRIMINATORS, VOTE_PROGRAM_ID
from dataclasses import dataclass


@dataclass
class BlockMetric:
    """Class for storing block metrics data"""
    block_id: int
    block_timestamp: datetime
    block_hash: str
    total_txns: int
    total_non_vote_txns: int
    total_vote_txns: int
    total_fees: int
    total_compute: int


class BlockMetricsProcessor:
    def process_block_metrics(self, block_data: dict) -> BlockMetric:
        """Process raw block data and extract relevant metrics.

        Args:
            block_data (dict): Raw block data from Solana RPC containing block information
                and transaction details.

        Returns:
            BlockMetric: A BlockMetric object containing processed metrics for the block.
        """
        # Extract block metadata
        block_info = block_data.get("result", {})
        block_id = block_info.get("parentSlot") + 1
        block_timestamp = datetime.fromtimestamp(block_info.get("blockTime", 0))
        block_hash = block_info.get("blockhash")

        # Initialize metrics
        total_txns = 0
        total_fees = 0
        total_compute = 0
        vote_txns = 0
        non_vote_txns = 0

        # Process each transaction to compute metrics
        if "transactions" in block_info:
            transactions = block_info["transactions"]
            total_txns = len(transactions)

            for txn in transactions:
                meta = txn.get("meta", {})
                total_fees += meta.get("fee", 0)
                total_compute += meta.get("computeUnitsConsumed", 0)

                if self.is_vote_txn(txn):
                    vote_txns += 1
                else:
                    non_vote_txns += 1

        return BlockMetric(
            block_id=block_id,
            block_timestamp=block_timestamp,
            block_hash=block_hash,
            total_txns=total_txns,
            total_non_vote_txns=non_vote_txns,
            total_vote_txns=vote_txns,
            total_fees=total_fees,
            total_compute=total_compute,
        )

    def is_vote_txn(self, transaction: dict) -> bool:
        """Determine if a transaction is a vote transaction.

        A vote transaction is identified by checking if it contains any instructions
        that are executed by the vote program and have a vote instruction discriminator.
        
        This follows the Solana is_simple_vote.
        https://docs.rs/solana-program/2.1.13/src/solana_program/vote/instruction.rs.html#168-180 

        Args:
            transaction (dict): Transaction data containing message and metadata.

        Returns:
            bool: True if the transaction is a vote transaction, False otherwise.
        """
        msg = transaction.get("transaction", {}).get("message", {})
        account_keys = msg.get("accountKeys", [])
        instructions = msg.get("instructions", [])
        is_vote_txn = False

        for instruction in instructions:
            program_id_index = instruction.get("programIdIndex")
            executing_account = (
                account_keys[program_id_index]
                if program_id_index is not None and program_id_index < len(account_keys)
                else None
            )
            base58_data = instruction.get("data", "")

            # Attempt base58 decoding
            try:
                decoded_bytes = base58.b58decode(base58_data)
            except Exception as e:
                decoded_bytes = b""
                print(f"Failed to decode: {str(e)}")

            # Check if instruction is a vote discriminator
            if (
                executing_account == VOTE_PROGRAM_ID
                and len(decoded_bytes) >= 4
                and decoded_bytes[:4] in VOTE_INSTRUCTION_DISCRIMINATORS
            ):
                is_vote_txn = True

        return is_vote_txn

    def prepare_metrics_data(self, raw_blocks: list[tuple[int, str]]) -> list[tuple]:
        """Process multiple raw blocks and prepare their metrics for database insertion.

        Args:
            raw_blocks (list[tuple[int, str]]): List of tuples containing (block_id, raw_json)
                where raw_json is the JSON string representation of the block data.

        Returns:
            list[tuple]: List of tuples ready for database insertion, where each tuple contains:
                (block_id, block_timestamp, block_hash, total_txns, total_non_vote_txns,
                total_vote_txns, total_fees, total_compute)

        Note:
            Blocks that fail to process will be logged and skipped.
        """
        block_metrics_data = []
        for block_id, raw_json in raw_blocks:
            try:
                # Parse the raw JSON
                block_data = json.loads(raw_json)
                metrics = self.process_block_metrics(block_data)

                # Prepare tuple for insertion
                block_metrics_data.append(
                    (
                        metrics.block_id,
                        metrics.block_timestamp,
                        metrics.block_hash,
                        metrics.total_txns,
                        metrics.total_non_vote_txns,
                        metrics.total_vote_txns,
                        metrics.total_fees,
                        metrics.total_compute,
                    )
                )

            except Exception as e:
                print(f"Error processing block {block_id}: {e}")

        return block_metrics_data
