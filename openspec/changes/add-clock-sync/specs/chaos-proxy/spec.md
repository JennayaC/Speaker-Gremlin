# Spec Delta

## ADDED Requirements

### Requirement: Relay time requests
The chaos proxy SHALL forward every `TIME_REQUEST` from a node to the coordinator. Drop (`--drop`), delay (`--max-delay`), and the isolation window (`--wait-after` / `--isolate-for`) SHALL NOT apply to time requests; they stay heartbeat-only. The proxy SHALL print a line saying it forwarded a time request, separate from its heartbeat lines.

#### Scenario: Time request forwarded
- **WHEN** NodeC sends a `TIME_REQUEST` to the proxy and no `--sync-delay` is given
- **THEN** the proxy forwards it to the coordinator right away and prints that it forwarded a time request from NodeC

#### Scenario: Heartbeat chaos does not touch time requests
- **WHEN** the proxy is started with `--target-node NodeA --drop 0.7 --max-delay 3.5`
- **AND** NodeA sends a `TIME_REQUEST`
- **THEN** the proxy forwards it to the coordinator without dropping or delaying it

### Requirement: Sync delay
The chaos proxy SHALL accept an optional `--sync-delay` switch (seconds, default 0). When it is above 0, the proxy SHALL hold each `TIME_REQUEST` for a random time between 0 and that many seconds before forwarding it, and print the delay it used. It SHALL apply to every node and SHALL NOT delay heartbeats or PLAY. The startup line SHALL show the sync delay.

#### Scenario: Time requests delayed
- **WHEN** the proxy is started with `--sync-delay 0.5`
- **AND** a node sends a `TIME_REQUEST`
- **THEN** the proxy forwards it to the coordinator after a random delay of at most 500 ms, and prints that delay

#### Scenario: Heartbeats not delayed by sync delay
- **WHEN** the proxy is started with only `--sync-delay 0.5`
- **THEN** heartbeats are forwarded to the coordinator with no delay

#### Scenario: Off by default
- **WHEN** the proxy is started without `--sync-delay`
- **THEN** time requests are forwarded with no delay
