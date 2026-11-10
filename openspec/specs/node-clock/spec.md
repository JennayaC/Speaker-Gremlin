# node-clock Specification

## Purpose
Each speaker node keeps its own simulated local clock that runs slightly fast or slow by a configurable amount (drift). This makes clock disagreement between nodes visible in the logs, the same way independent hardware oscillators disagree on real devices.

## Requirements

### Requirement: Drift configuration
The speaker node SHALL accept an optional third positional command-line argument giving its clock drift in parts per million (PPM), and SHALL use a drift of 0 PPM when the argument is omitted.

#### Scenario: Drift provided
- **WHEN** a node is started as `speaker_node.py NodeC 5005 -100`
- **THEN** the node's clock runs 100 PPM slower than real time

#### Scenario: Drift omitted
- **WHEN** a node is started as `speaker_node.py NodeA 5003`
- **THEN** the node's clock runs at the same rate as real time

### Requirement: Initial alignment
The node clock SHALL read the same value as the host wall clock at the moment the node process starts.

#### Scenario: Clock at startup
- **WHEN** a node process starts
- **THEN** its clock reading equals the host wall clock time, with zero offset

### Requirement: Drift accumulation
The node clock SHALL advance at a rate of (1 + drift / 1,000,000) times real elapsed time, measured from the host's monotonic clock, so that clock error grows linearly with time.

#### Scenario: Fast clock after 100 seconds
- **WHEN** a node configured with +100 PPM has been running for 100 real seconds
- **THEN** its clock reads 10 ms ahead of the host wall clock

#### Scenario: Host wall clock is adjusted
- **WHEN** the host's wall clock is changed while a node is running
- **THEN** the node clock does not jump, because it advances from the monotonic clock

### Requirement: Clock usage
The speaker node SHALL use its simulated clock, not the host wall clock, for every timestamp it sends and every scheduling decision it makes.

#### Scenario: Heartbeat timestamp
- **WHEN** a node sends a HEARTBEAT
- **THEN** the `sender_ts` field contains the node clock's current reading

#### Scenario: Waiting for play_at
- **WHEN** a node receives a PLAY or STATE_SNAPSHOT with a `play_at` time
- **THEN** it computes how long to wait by comparing `play_at` against its own clock
