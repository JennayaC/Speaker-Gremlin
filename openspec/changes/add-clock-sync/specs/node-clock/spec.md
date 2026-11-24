# Spec Delta

## MODIFIED Requirements

### Requirement: Clock usage
The speaker node SHALL use its simulated clock, not the host wall clock, for every timestamp it sends and every scheduling decision it makes. With sync on (see the `clock-sync` capability), "its simulated clock" means the synced clock (the raw drifting clock plus the corrections from syncing); the raw clock is only reported, never used for scheduling. With sync off, the synced clock and the raw clock are the same.

#### Scenario: Heartbeat timestamp
- **WHEN** a node sends a HEARTBEAT
- **THEN** the `sender_ts` field contains the node's synced clock reading (equal to the raw clock when sync is off)

#### Scenario: Raw clock reported with sync on
- **WHEN** a node with sync on sends a HEARTBEAT
- **THEN** the `raw_ts` field contains the raw drifting clock reading

#### Scenario: Waiting for play_at
- **WHEN** a node receives a PLAY or STATE_SNAPSHOT with a `play_at` time
- **THEN** it computes how long to wait by comparing `play_at` against its synced clock
