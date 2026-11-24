# Spec Delta

## ADDED Requirements

### Requirement: Experiment B setup
When started with `--experiment B`, the launcher SHALL start the coordinator, a chaos proxy that sends every PLAY command twice, and the three speaker nodes.

#### Scenario: Run Experiment B
- **WHEN** the user runs `python src/run_cluster.py --experiment B`
- **THEN** the coordinator and the three nodes start
- **AND** the chaos proxy starts with `--duplicate 1.0`

## MODIFIED Requirements

### Requirement: Unknown experiment name rejected
When given an `--experiment` name it does not know, the launcher SHALL print an error that lists the valid names and SHALL start no processes.

#### Scenario: Typo in name
- **WHEN** the user runs `python src/run_cluster.py --experiment Z`
- **THEN** an error is printed naming the valid choices (A, B, C)
- **AND** no coordinator, proxy, or node process is started
