# Reference: https://docs.rs/solana-program/2.1.13/src/solana_program/vote/instruction.rs.html
VOTE_INSTRUCTION_DISCRIMINATORS = {
    b"\x02\x00\x00\x00",  # vote
    b"\x06\x00\x00\x00",  # voteSwitch
    b"\x08\x00\x00\x00",  # updateVoteState
    b"\x09\x00\x00\x00",  # updateVoteStateSwitch
    b"\x0c\x00\x00\x00",  # compactUpdateVoteState
    b"\x0d\x00\x00\x00",  # compactUpdateVoteStateSwitch
    b"\x0e\x00\x00\x00",  # towerSync
    b"\x0f\x00\x00\x00",  # towerSyncSwitch
}

VOTE_PROGRAM_ID = "Vote111111111111111111111111111111111111111"
