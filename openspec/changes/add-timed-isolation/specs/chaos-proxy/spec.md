# Spec Delta

## Purpose

The chaos proxy sits between the speaker nodes and the coordinator and breaks the traffic on purpose (drops, delays, isolation), so that distributed-systems failures can be seen and repeated.

## ADDED Requirements

### Requirement: Timed isolation window
The chaos proxy SHALL accept two optional switches, `--isolate-after` (seconds) and `--isolate-for` (seconds). It SHALL drop every packet from the targeted node(s) that arrives at least `--isolate-after` seconds and less than `--isolate-after` + `--isolate-for` seconds after the proxy started.

#### Scenario: Node cut off during the window
- **WHEN** the proxy is started with `--target-node NodeA --isolate-after 5 --isolate-for 10`
- **AND** a heartbeat from NodeA arrives 8 seconds after the proxy started
- **THEN** the proxy drops that heartbeat and does not forward it to the coordinator

#### Scenario: Node not cut off before the window
- **WHEN** the proxy is started with `--target-node NodeA --isolate-after 5 --isolate-for 10`
- **AND** a heartbeat from NodeA arrives 2 seconds after the proxy started
- **THEN** the proxy forwards it to the coordinator

#### Scenario: Node back after the window
- **WHEN** the proxy is started with `--target-node NodeA --isolate-after 5 --isolate-for 10`
- **AND** a heartbeat from NodeA arrives 16 seconds after the proxy started
- **THEN** the proxy forwards it to the coordinator

### Requirement: Isolation follows the target rule
The isolation window SHALL use the same target rule as `--drop`: it applies only to the node named by `--target-node`, or to every node when `--target-node` is not given.

#### Scenario: Other nodes keep talking
- **WHEN** the proxy is started with `--target-node NodeA --isolate-after 5 --isolate-for 10`
- **AND** a heartbeat from NodeB arrives 8 seconds after the proxy started
- **THEN** the proxy forwards it to the coordinator

### Requirement: Isolation off by default
When `--isolate-for` is not given or is 0, the proxy SHALL not isolate any node, and SHALL behave as it did before this change.

#### Scenario: No isolation switches
- **WHEN** the proxy is started with only `--drop 0.2`
- **THEN** no node is ever cut off by a time window, and packets are dropped only by the 20% random drop

#### Scenario: Start time only
- **WHEN** the proxy is started with `--target-node NodeA --isolate-after 5` and no `--isolate-for`
- **THEN** NodeA is never cut off by a time window
