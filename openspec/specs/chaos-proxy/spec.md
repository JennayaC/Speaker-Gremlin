# chaos-proxy Specification

## Purpose

The chaos proxy sits between the speaker nodes and the coordinator and breaks the traffic on purpose (drops, delays, isolation), so that distributed-systems failures can be seen and repeated.

## Requirements

### Requirement: Timed isolation window
The chaos proxy SHALL accept two optional switches, `--wait-after` (seconds) and `--isolate-for` (seconds). It SHALL drop every packet from the targeted node(s) that arrives at least `--wait-after` seconds and less than `--wait-after` + `--isolate-for` seconds after the proxy started.

#### Scenario: Node cut off during the window
- **WHEN** the proxy is started with `--target-node NodeA --wait-after 5 --isolate-for 10`
- **AND** a heartbeat from NodeA arrives 8 seconds after the proxy started
- **THEN** the proxy drops that heartbeat and does not forward it to the coordinator

#### Scenario: Node not cut off before the window
- **WHEN** the proxy is started with `--target-node NodeA --wait-after 5 --isolate-for 10`
- **AND** a heartbeat from NodeA arrives 2 seconds after the proxy started
- **THEN** the proxy forwards it to the coordinator

#### Scenario: Node back after the window
- **WHEN** the proxy is started with `--target-node NodeA --wait-after 5 --isolate-for 10`
- **AND** a heartbeat from NodeA arrives 16 seconds after the proxy started
- **THEN** the proxy forwards it to the coordinator

### Requirement: Isolation follows the target rule
The isolation window SHALL use the same target rule as `--drop`: it applies only to the node named by `--target-node`, or to every node when `--target-node` is not given.

#### Scenario: Other nodes keep talking
- **WHEN** the proxy is started with `--target-node NodeA --wait-after 5 --isolate-for 10`
- **AND** a heartbeat from NodeB arrives 8 seconds after the proxy started
- **THEN** the proxy forwards it to the coordinator

### Requirement: Isolation off by default
When `--isolate-for` is not given or is 0, the proxy SHALL not isolate any node, and SHALL behave as it did before this change.

#### Scenario: No isolation switches
- **WHEN** the proxy is started with only `--drop 0.2`
- **THEN** no node is ever cut off by a time window, and packets are dropped only by the 20% random drop

#### Scenario: Start time only
- **WHEN** the proxy is started with `--target-node NodeA --wait-after 5` and no `--isolate-for`
- **THEN** NodeA is never cut off by a time window

### Requirement: Relay PLAY commands to nodes
The chaos proxy SHALL accept PLAY commands from the coordinator and forward each one to the speaker node it is addressed to. The coordinator SHALL send PLAY to the chaos proxy, not straight to the nodes.

#### Scenario: PLAY reaches its node through the proxy
- **WHEN** the coordinator sends a PLAY addressed to NodeB
- **THEN** the chaos proxy forwards it to NodeB
- **AND** NodeB prints `Received PLAY command, scheduled for: ...`

#### Scenario: Each node gets its own PLAY
- **WHEN** the coordinator sends PLAY to all three nodes through the proxy
- **THEN** NodeA, NodeB, and NodeC each receive exactly one PLAY (when `--duplicate` is 0)

### Requirement: PLAY is not affected by heartbeat chaos
Drop (`--drop`), delay (`--max-delay`), and the isolation window (`--wait-after` / `--isolate-for`) SHALL apply only to heartbeats. The proxy SHALL never drop or delay a PLAY command.

#### Scenario: Experiment A still delivers PLAY
- **WHEN** the proxy is started with `--target-node NodeA --max-delay 3.5 --drop 0.7`
- **AND** the coordinator sends PLAY to NodeA
- **THEN** the proxy forwards it to NodeA right away, without dropping or delaying it

#### Scenario: PLAY during isolation
- **WHEN** the proxy is started with `--target-node NodeA --wait-after 5 --isolate-for 10`
- **AND** a PLAY for NodeA arrives 8 seconds after the proxy started
- **THEN** the proxy forwards it to NodeA

### Requirement: Duplicate mode
The chaos proxy SHALL accept an optional `--duplicate` switch, a chance from 0.0 to 1.0. For each PLAY it relays, the proxy SHALL send it to the node a second time with that chance, and print a line saying it duplicated the PLAY. The default is 0.0 (never duplicate). Duplicate mode SHALL apply to every node; `--target-node` does not limit it.

#### Scenario: Always duplicate
- **WHEN** the proxy is started with `--duplicate 1.0`
- **AND** the coordinator sends a PLAY to NodeA
- **THEN** NodeA receives the same PLAY twice
- **AND** the proxy prints that it duplicated the PLAY for NodeA

#### Scenario: Node drops the duplicate
- **WHEN** the proxy is started with `--duplicate 1.0`
- **AND** a node receives the same PLAY (cmd_seq 1) twice
- **THEN** the node applies the first one
- **AND** prints `Drop redundant PLAY command (seq 1). Last applied: 1` for the second one

#### Scenario: Duplicate off by default
- **WHEN** the proxy is started without `--duplicate`
- **THEN** every PLAY is sent to its node exactly once

#### Scenario: Duplicates do not touch heartbeats
- **WHEN** the proxy is started with `--duplicate 1.0`
- **THEN** heartbeats are forwarded to the coordinator once each, as before
