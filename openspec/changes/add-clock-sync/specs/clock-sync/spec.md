# Spec Delta

## Purpose

Speaker nodes keep their drifting clocks in step with the coordinator by regularly asking it for the time and correcting themselves using the round-trip time (Cristian's algorithm, the simple idea behind NTP). The raw drift stays visible next to the corrected clock so the effect of syncing can be seen.

## ADDED Requirements

### Requirement: Sync switch
The speaker node SHALL accept an optional `--sync` switch. Without it, the node SHALL NOT send time requests and SHALL behave exactly as before this change. The switch SHALL work whether or not a drift value is given.

#### Scenario: Sync on with drift
- **WHEN** a node is started as `speaker_node.py NodeC 5005 -10000 --sync`
- **THEN** the node's raw clock runs 10000 PPM slow and the node syncs its clock

#### Scenario: Sync on without drift
- **WHEN** a node is started as `speaker_node.py NodeA 5003 --sync`
- **THEN** the node starts with 0 PPM drift and syncs its clock

#### Scenario: Sync off by default
- **WHEN** a node is started as `speaker_node.py NodeB 5004 50`
- **THEN** it sends no time requests and its heartbeats have no `raw_ts` field

### Requirement: Time request and reply
With sync on, the node SHALL send a `TIME_REQUEST` to the chaos proxy every 5 seconds, carrying its node name, its port, and the time it sent the request by its own synced clock. The coordinator SHALL answer each `TIME_REQUEST` with a `TIME_REPLY` sent straight to the node's port, carrying the request's send time unchanged and the coordinator's current time. The coordinator SHALL NOT treat a `TIME_REQUEST` as a heartbeat.

#### Scenario: Coordinator answers
- **WHEN** the coordinator receives a `TIME_REQUEST` from NodeC (port 5005)
- **THEN** it sends a `TIME_REPLY` to port 5005 containing the request's send time and its own current time

#### Scenario: Time request is not a heartbeat
- **WHEN** the coordinator receives a `TIME_REQUEST`
- **THEN** it does not print an `Expected | Local | Error` line for it, and does not change packet-loss or lost-node tracking

### Requirement: Clock correction
When the node receives a `TIME_REPLY`, it SHALL compute the round-trip time (its synced clock now − the request's send time), estimate the coordinator's time right now as the reply's coordinator time + half the round-trip time, and shift its synced clock by the difference between that estimate and its synced clock now. It SHALL print the round-trip time and the correction it applied. The raw clock SHALL NOT be changed.

#### Scenario: Slow clock pulled forward
- **WHEN** NodeC's synced clock is 50 ms behind the coordinator and a sync completes with a round trip near 0 ms
- **THEN** NodeC's synced clock moves forward by about 50 ms
- **AND** NodeC prints the round-trip time and a correction of about +50 ms

#### Scenario: Raw clock keeps drifting
- **WHEN** a node with sync on has run for 100 seconds at −10000 PPM
- **THEN** its raw clock is about 1 second behind real time, whatever corrections were applied to the synced clock

### Requirement: Raw and synced error side by side
With sync on, each heartbeat SHALL carry the raw clock reading in a `raw_ts` field in addition to `sender_ts`. When a heartbeat has `raw_ts`, the coordinator SHALL print one line per heartbeat showing both the raw error and the synced error in milliseconds, each measured against the coordinator's receive time. Heartbeats without `raw_ts` SHALL be printed as before.

#### Scenario: Both errors shown
- **WHEN** the coordinator receives a heartbeat from NodeC that has `raw_ts`
- **THEN** it prints a line naming NodeC with a raw error and a synced error, e.g. `Raw error: -312.0ms | Synced error: +0.4ms`

#### Scenario: Old output kept
- **WHEN** the coordinator receives a heartbeat without `raw_ts`
- **THEN** it prints the same `Expected | Local | Error` line as before this change

### Requirement: Uneven delay makes sync wrong
The correction SHALL assume the trip to the coordinator and the trip back take equal time. When only the trip to the coordinator is delayed, the synced clock SHALL end up ahead of the coordinator by about half of that extra delay, and this SHALL be visible in the synced error.

#### Scenario: Delayed request
- **WHEN** a `TIME_REQUEST` is held up 400 ms on the way to the coordinator and the reply comes straight back
- **THEN** after that sync the node's synced clock is about 200 ms ahead of the coordinator
- **AND** the coordinator's synced error for that node shows roughly +200 ms
