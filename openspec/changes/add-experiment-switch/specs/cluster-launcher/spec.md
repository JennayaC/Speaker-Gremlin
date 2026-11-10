# Spec Delta

## Purpose

The cluster launcher (`src/run_cluster.py`) starts the coordinator, chaos proxy, and speaker nodes from one terminal, and can start them in a named experiment setup so experiments are repeatable without editing code.

## ADDED Requirements

### Requirement: Normal run with no experiment
When started with no `--experiment` switch, the launcher SHALL start the coordinator, a chaos proxy with no drops, delay, or isolation, and the three speaker nodes (NodeA drift 0, NodeB drift 50, NodeC drift -100).

#### Scenario: Plain run
- **WHEN** the user runs `python src/run_cluster.py`
- **THEN** the coordinator, a plain chaos proxy, and NodeA, NodeB, NodeC all start

### Requirement: Experiment A setup
When started with `--experiment A`, the launcher SHALL start the coordinator, a chaos proxy that delays NodeA's packets by a random amount up to 3.5 seconds, and the three speaker nodes.

#### Scenario: Run Experiment A
- **WHEN** the user runs `python src/run_cluster.py --experiment A`
- **THEN** the coordinator and the three nodes start
- **AND** the chaos proxy starts with `--target-node NodeA --max-delay 3.5`

### Requirement: Experiment C setup
When started with `--experiment C`, the launcher SHALL start a chaos proxy that cuts off NodeA from 5 to 15 seconds after it starts, and the three speaker nodes. It SHALL NOT start the coordinator.

#### Scenario: Run Experiment C
- **WHEN** the user runs `python src/run_cluster.py --experiment C`
- **THEN** the three nodes start
- **AND** the chaos proxy starts with `--target-node NodeA --wait-after 5 --isolate-for 10`
- **AND** no coordinator process is started by the launcher

### Requirement: Unknown experiment name rejected
When given an `--experiment` name it does not know, the launcher SHALL print an error that lists the valid names and SHALL start no processes.

#### Scenario: Typo in name
- **WHEN** the user runs `python src/run_cluster.py --experiment Z`
- **THEN** an error is printed naming the valid choices (A, C)
- **AND** no coordinator, proxy, or node process is started

### Requirement: Clean shutdown
On Ctrl+C the launcher SHALL stop every process it started, whichever experiment was chosen.

#### Scenario: Stop during Experiment C
- **WHEN** the user presses Ctrl+C while `--experiment C` is running
- **THEN** the proxy and all three nodes stop
- **AND** a coordinator started separately in another terminal is not touched
