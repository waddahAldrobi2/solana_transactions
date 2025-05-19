import pytest
from datetime import datetime
import json
from block_metrics_processor import BlockMetricsProcessor, BlockMetric
from constants import VOTE_PROGRAM_ID, VOTE_INSTRUCTION_DISCRIMINATORS


@pytest.fixture
def processor():
    return BlockMetricsProcessor()


@pytest.fixture
def sample_block_data():
    return {
        "result": {
            "parentSlot": 100,
            "blockTime": 1634567890,
            "blockhash": "test_hash_123",
            "transactions": [
                {
                    "meta": {"fee": 5000, "computeUnitsConsumed": 1000},
                    "transaction": {
                        "message": {
                            "accountKeys": ["some_account", VOTE_PROGRAM_ID],
                            "instructions": [
                                {
                                    "programIdIndex": 1,
                                    "data": "JnrP9",  # compactUpdateVoteState
                                }
                            ],
                        }
                    },
                },
                {
                    "meta": {"fee": 3000, "computeUnitsConsumed": 500},
                    "transaction": {
                        "message": {
                            "accountKeys": ["some_account", "other_account"],
                            "instructions": [{"programIdIndex": 1, "data": "somedata"}],
                        }
                    },
                },
            ],
        }
    }


def test_process_block_metrics(processor, sample_block_data):
    metrics = processor.process_block_metrics(sample_block_data)

    assert isinstance(metrics, BlockMetric)
    assert metrics.block_id == 101  # parentSlot + 1
    assert isinstance(metrics.block_timestamp, datetime)
    assert metrics.block_hash == "test_hash_123"
    assert metrics.total_txns == 2
    assert metrics.total_vote_txns == 1
    assert metrics.total_non_vote_txns == 1
    assert metrics.total_fees == 8000  # 5000 + 3000
    assert metrics.total_compute == 1500  # 1000 + 500


def test_is_vote_txn(processor):
    # Test vote transaction
    vote_txn = {
        "transaction": {
            "message": {
                "accountKeys": ["some_account", VOTE_PROGRAM_ID],
                "instructions": [
                    {"programIdIndex": 1, "data": "JnrP9"}  # compactUpdateVoteState
                ],
            }
        }
    }
    assert processor.is_vote_txn(vote_txn) is True

    # Test non-vote transaction
    non_vote_txn = {
        "transaction": {
            "message": {
                "accountKeys": ["some_account", "other_account"],
                "instructions": [{"programIdIndex": 1, "data": "somedata"}],
            }
        }
    }
    assert processor.is_vote_txn(non_vote_txn) is False


def test_prepare_metrics_data(processor, sample_block_data):
    raw_blocks = [
        (101, json.dumps(sample_block_data)),
        (102, json.dumps(sample_block_data)),
    ]

    metrics_data = processor.prepare_metrics_data(raw_blocks)

    assert len(metrics_data) == 2
    for block_metrics in metrics_data:
        assert len(block_metrics) == 8  # All fields present
        assert block_metrics[0] in [101, 102]  # block_id
        assert isinstance(block_metrics[1], datetime)  # block_timestamp
        assert block_metrics[2] == "test_hash_123"  # block_hash
        assert block_metrics[3] == 2  # total_txns
        assert block_metrics[4] == 1  # total_non_vote_txns
        assert block_metrics[5] == 1  # total_vote_txns
        assert block_metrics[6] == 8000  # total_fees
        assert block_metrics[7] == 1500  # total_compute
